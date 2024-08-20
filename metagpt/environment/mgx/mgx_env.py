from __future__ import annotations

from metagpt.actions import (
    UserRequirement,
    WriteDesign,
    WritePRD,
    WriteTasks,
    WriteTest,
)
from metagpt.actions.summarize_code import SummarizeCode
from metagpt.const import AGENT, IMAGES
from metagpt.environment.base_env import Environment
from metagpt.logs import get_human_input
from metagpt.roles import Architect, ProductManager, ProjectManager, Role
from metagpt.schema import Message, SerializationMixin
from metagpt.utils.common import any_to_str, any_to_str_set, extract_and_encode_images


class MGXEnv(Environment, SerializationMixin):
    """MGX Environment"""

    # If True, fixed software sop bypassing TL is allowed, otherwise, TL will fully take over the routing
    allow_bypass_team_leader: bool = False

    direct_chat_roles: set[str] = set()  # record direct chat: @role_name

    def _publish_message(self, message: Message, peekable: bool = True) -> bool:
        return super().publish_message(message, peekable)

    def publish_message(self, message: Message, user_defined_recipient: str = "", publicer: str = "") -> bool:
        """let the team leader take over message publishing"""
        message = self.attach_images(message)  # for multi-modal message

        tl = self.get_role("Mike")  # TeamLeader's name is Mike

        if user_defined_recipient:
            # human user's direct chat message to a certain role
            for role_name in message.send_to:
                if self.get_role(role_name).is_idle:
                    # User starts a new direct chat with a certain role, expecting a direct chat response from the role; Other roles including TL should not be involved.
                    # If the role is not idle, it means the user helps the role with its current work, in this case, we handle the role's response message as usual.
                    self.direct_chat_roles.add(role_name)

            self._publish_message(message)
            # # bypass team leader, team leader only needs to know but not to react (commented out because TL doesn't understand the message well in actual experiments)
            # tl.rc.memory.add(self.move_message_info_to_content(message))

        elif message.sent_from in self.direct_chat_roles:
            # direct chat response from a certain role to human user, team leader and other roles in the env should not be involved, no need to publish
            self.direct_chat_roles.remove(message.sent_from)

        elif (
            self.allow_bypass_team_leader
            and self.message_within_software_sop(message)
            and not self.has_user_requirement()
        ):
            # Quick routing for messages within software SOP, bypassing TL.
            # Use rules to check for user intervention and to finish task.
            # NOTE: This escapes TL's supervision and has pitfalls such as routing obsolete messages even if TL has acquired a new user requirement.
            #       In addition, we should not determine the status of a task based on message cause_by.
            #       Consider replacing this in the future.
            self._publish_message(message)
            if self.is_software_task_finished(message):
                tl.rc.memory.add(self.move_message_info_to_content(message))
                from metagpt.utils.report import CURRENT_ROLE

                role = CURRENT_ROLE.get(None)
                if role:
                    CURRENT_ROLE.set(tl)
                    tl.finish_current_task()
                    CURRENT_ROLE.set(role)
                else:
                    tl.finish_current_task()

        elif publicer == tl.profile:
            if message.send_to == {"no one"}:
                # skip the dummy message from team leader
                return True
            # message processed by team leader can be published now
            self._publish_message(message)

        else:
            # every regular message goes through team leader
            message = self.move_message_info_to_content(message)
            message.send_to.add(tl.name)
            tl.put_message(message)

        self.history.add(message)

        return True

    async def ask_human(self, question: str, sent_from: Role = None) -> str:
        # NOTE: Can be overwritten in remote setting
        rsp = await get_human_input(question)
        return "Human response: " + rsp

    async def reply_to_human(self, content: str, sent_from: Role = None) -> str:
        # NOTE: Can be overwritten in remote setting
        return "SUCCESS, human has received your reply. Refrain from resending duplicate messages."

    def message_within_software_sop(self, message: Message) -> bool:
        # Engineer, QaEngineer can be end of the SOP. Their msg requires routing outside.
        members_concerned = [ProductManager, Architect, ProjectManager]
        return message.sent_from in any_to_str_set(members_concerned)

    def has_user_requirement(self, k=1) -> bool:
        """A heuristics to check if there is a recent user intervention"""
        return any_to_str(UserRequirement) in [msg.cause_by for msg in self.history.get(k)]

    def is_software_task_finished(self, message: Message) -> bool:
        """Use a hard-coded rule to check if one software task is finished"""
        return message.cause_by in any_to_str_set([WritePRD, WriteDesign, WriteTasks, SummarizeCode]) or (
            message.cause_by == any_to_str(WriteTest) and "Exceeding" in message.content
        )

    def move_message_info_to_content(self, message: Message) -> Message:
        """Two things here:
        1. Convert role, since role field must be reserved for LLM API, and is limited to, for example, one of ["user", "assistant", "system"]
        2. Add sender and recipient info to content, making TL aware, since LLM API only takes content as input
        """
        converted_msg = message.model_copy(deep=True)
        if converted_msg.role not in ["system", "user", "assistant"]:
            converted_msg.role = "assistant"
        sent_from = converted_msg.metadata[AGENT] if AGENT in converted_msg.metadata else converted_msg.sent_from
        converted_msg.content = (
            f"[Message] from {sent_from or 'User'} to {converted_msg.send_to}: {converted_msg.content}"
        )
        return converted_msg

    def attach_images(self, message: Message) -> Message:
        if message.role == "user":
            images = extract_and_encode_images(message.content)
            if images:
                message.add_metadata(IMAGES, images)
        return message

    def __repr__(self):
        return "MGXEnv()"