#!/usr/bin/env python3
# Copyright (c) 2024 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test the listmempooltransactions RPC."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    assert_equal,
    assert_greater_than,
)
from test_framework.wallet import MiniWallet


class ListMempoolTransactionsTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1

    def run_test(self):
        self.log.info("Initialize wallet and get UTXO")
        self.wallet = MiniWallet(self.nodes[0])
        utxo = self.wallet.get_utxo()

        self.log.info("Test empty mempool initially")
        empty_result = self.nodes[0].listmempooltransactions(0)
        self.log.info(f"Empty mempool result: {empty_result}")
        assert_equal(empty_result["txs"], [])
        initial_sequence = empty_result["mempool_sequence"]

        self.log.info("Add first transaction to mempool")
        tx1 = self.wallet.send_self_transfer(from_node=self.nodes[0])
        tx1_hash = tx1["txid"]

        self.log.info("Check first transaction is in mempool")
        result_after_tx1 = self.nodes[0].listmempooltransactions(0)
        self.log.info(f"Result after tx1: {result_after_tx1}")
        assert_equal(len(result_after_tx1["txs"]), 1)
        assert_equal(result_after_tx1["txs"][0]["txid"], tx1_hash)
        sequence_after_tx1 = result_after_tx1["mempool_sequence"]
        assert_greater_than(sequence_after_tx1, initial_sequence)

        self.log.info("Add second transaction to mempool")
        tx2 = self.wallet.send_self_transfer(from_node=self.nodes[0])
        tx2_hash = tx2["txid"]

        self.log.info("Get all transactions from start")
        all_txs_result = self.nodes[0].listmempooltransactions(0)
        self.log.info(f"All transactions result: {all_txs_result}")
        assert_equal(len(all_txs_result["txs"]), 2)

        self.log.info("Test sequence filtering - get only transactions after first one")
        filtered_result = self.nodes[0].listmempooltransactions(sequence_after_tx1)
        self.log.info(f"Filtered result: {filtered_result}")
        assert_equal(len(filtered_result["txs"]), 1)
        assert_equal(filtered_result["txs"][0]["txid"], tx2_hash)


if __name__ == '__main__':
    ListMempoolTransactionsTest(__file__).main()
