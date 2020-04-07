from loopchain.blockchain.invoke_result import InvokeResult
from loopchain.blockchain.types import Hash32


class TestInvokeResult:
    def test_invoke_result(self):
        # GIVEN I have origin data of invoke result
        epoch_num = 1
        round_num = 1
        data_id = Hash32.fromhex("c71303ef8543d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238", ignore_prefix=True)
        tx_hash = Hash32.fromhex("a3e227cf2513d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238", ignore_prefix=True)
        invoke_result_dict = {
            "txResults": [
                {
                    "status": "0x1",
                    "txHash": tx_hash.hex(),
                    "txIndex": "0x0",
                    "blockHeight": "0x1234",
                    "blockHash": data_id.hex(),
                    "cumulativeStepUsed": "0x1234",
                    "stepUsed": "0x1234",
                    "stepPrice": "0x100",
                    "scoreAddress": "cxb0776ee37f5b45bfaea8cff1d8232fbb6122ec32"
                }
            ],
            "stateRootHash": "c71303ef8543d04b5dc1ba6579132b143087c68db1b2168786408fcbce568238",
            "addedTransactions": {
                "6804dd2ccd9a9d17136d687838aa09e02334cd4afa964d75993f18991ee874de": {
                    "version": "0x3",
                    "timestamp": "0x563a6cf330136",
                    "dataType": "base",
                    "data": {
                        "prep": {
                            "incentive": "0x1",
                            "rewardRate": "0x1",
                            "totalDelegation": "0x3872423746291",
                            "value": "0x7800000"
                        }
                    }
                }
            },
            "prep": {
                "preps": [
                    {
                        "id": "hx86aba2210918a9b116973f3c4b27c41a54d5dafe",
                        "p2pEndpoint": "123.45.67.89:7100"
                    },
                    {
                        "id": "hx13aca3210918a9b116973f3c4b27c41a54d5dad1",
                        "p2pEndPoint": "210.34.56.17:7100"
                    }
                ],
                "irep": "0x1",
                "state": "0x0",
                "rootHash": "c7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
            }
        }

        # WHEN I got InvokeResult
        invoke_result: InvokeResult = InvokeResult.from_dict(
            epoch_num=epoch_num,
            round_num=round_num,
            invoke_result=invoke_result_dict
        )

        # THEN tx results in InvokeResult should be identical with the origin values
        tx_results = invoke_result.receipts[tx_hash]
        tx_results_orig = invoke_result_dict["txResults"][0]
        assert tx_results["status"] == tx_results_orig["status"]
        assert tx_results["txHash"] == tx_results_orig["txHash"]
        assert tx_results["txIndex"] == tx_results_orig["txIndex"]
        assert tx_results["blockHeight"] == tx_results_orig["blockHeight"]
        assert tx_results["blockHash"] == tx_results_orig["blockHash"]
        assert tx_results["cumulativeStepUsed"] == tx_results_orig["cumulativeStepUsed"]
        assert tx_results["stepUsed"] == tx_results_orig["stepUsed"]
        assert tx_results["stepPrice"] == tx_results_orig["stepPrice"]
