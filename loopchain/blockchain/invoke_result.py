from typing import cast, OrderedDict, List, Optional

from lft.consensus.messages.message import MessagePool, Message

from loopchain.blockchain import Hash32
from loopchain.blockchain.blocks.v0_3 import BlockProver
from loopchain.blockchain.blocks import BlockProverType


class InvokeResult(Message):
    def __init__(self, epoch_num, round_num, receipts, state_hash, added_transactions, prep):
        self._id = b"0"  # No need to identify invoke results...
        self._epoch_num = epoch_num
        self._round_num = round_num

        self._receipts = receipts
        self._state_hash: Hash32 = state_hash
        self._added_transactions = added_transactions
        self._prep = prep

    @property
    def id(self) -> bytes:
        return self._id

    @property
    def epoch_num(self) -> int:
        return self._epoch_num

    @property
    def round_num(self) -> int:
        return self._round_num

    @property
    def receipts(self) -> dict:
        return self._receipts

    @property
    def receipt_hash(self) -> Hash32:
        if not self.receipts:
            return Hash32.empty()

        block_prover = BlockProver(self.receipts, BlockProverType.Receipt)
        return block_prover.get_proof_root()

    @property
    def state_hash(self) -> Hash32:
        return self._state_hash

    @property
    def added_transactions(self) -> OrderedDict:
        return self._added_transactions

    @property
    def prep(self) -> Optional[dict]:
        return self._prep

    @property
    def next_reps_hash(self) -> Hash32:
        if self.prep:
            return self.prep["rootHash"]
        else:
            return Hash32.empty()

    @classmethod
    def from_dict(cls, epoch_num: int, round_num: int, invoke_result: dict):
        tx_receipts_origin = invoke_result.get("txResults")
        if not isinstance(tx_receipts_origin, dict):
            receipts = {Hash32.fromhex(tx_receipt['txHash'], ignore_prefix=True): tx_receipt
                        for tx_receipt in cast(list, tx_receipts_origin)}
        else:
            receipts = tx_receipts_origin

        state_hash = Hash32(bytes.fromhex(invoke_result.get("stateRootHash")))
        added_transactions = invoke_result.get("addedTransactions")
        prep = invoke_result.get("prep")
        return cls(
            epoch_num=epoch_num,
            round_num=round_num,
            receipts=receipts,
            state_hash=state_hash,
            added_transactions=added_transactions,
            prep=prep
        )


class InvokeResultPool(MessagePool):
    def get_invoke_result(self, block_hash: Hash32) -> Message:
        return self.get_message(block_hash)

    def invoke(self,
               height: int,
               block_hash: Hash32,
               prev_block: 'Block',
               transactions,
               tx_versioner,
               timestamp,
               prev_votes,
               is_block_editable: bool = False) -> InvokeResult:
        """Originated from `Blockchain.score_invoke`."""

        icon_service = StubCollection().icon_score_stubs[ChannelProperty().name]

        request: InvokeRequest = InvokeRequest(
            height=height,
            transactions=transactions,
            prev_peer_id=prev_block.prev_id,
            prev_block_hash=prev_block.id,
            block_hash=block_hash,
            timestamp=timestamp,
            prev_votes=prev_votes,
            is_block_editable=is_block_editable,
            tx_versioner=tx_versioner
        )
        invoke_result: InvokeResult = InvokeResult.from_dict(icon_service.sync_task().invoke(request))
        self.add_message(invoke_result)

        return invoke_result
