from typing import TYPE_CHECKING
from lft.event import EventSystem, EventRegister
from lft.consensus import Consensus
from lft.consensus.events import BroadcastDataEvent, BroadcastVoteEvent, ReceiveDataEvent, ReceiveVoteEvent


if TYPE_CHECKING:
    from loopchain.blockchain.types import ExternalAddress
    from loopchain.baseservice import BroadcastScheduler
    from lft.consensus.messages.data import DataFactory, Data
    from lft.consensus.messages.vote import VoteFactory, Vote


class ConsensusRunner(EventRegister):
    def __init__(self, node_id: 'ExternalAddress', event_system: 'EventSystem',
                 data_factory: 'DataFactory', vote_factory: 'VoteFactory', broadcast_scheduler: 'BroadcastScheduler'):
        self.broadcast_scheduler = broadcast_scheduler
        self.event_system = event_system
        self.consensus = Consensus(self.event_system, node_id, data_factory, vote_factory)
        super().__init__(self.event_system.simulator)

    def start(self):
        self.event_system.start()

    async def _on_event_broadcast_data(self, block: 'Data'):
        # call broadcast block
        pass

    async def _on_event_broadcast_vote(self, vote: 'Vote'):
        # call broadcast vote
        pass

    async def _on_event_receive_data(self, block: 'Data'):
        await self.consensus.receive_data(block)

    async def _on_event_receive_vote(self, vote: 'Vote'):
        await self.consensus.receive_vote(vote)

    _handler_prototypes = {
        BroadcastDataEvent, _on_event_broadcast_data,
        BroadcastVoteEvent, _on_event_broadcast_vote,
        ReceiveDataEvent, _on_event_receive_data,
        ReceiveVoteEvent, _on_event_receive_vote
    }
