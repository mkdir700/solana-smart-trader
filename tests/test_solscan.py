from re import S
import pytest

from common.solscan import AsyncSolcan


class TestSolscan:
    @pytest.mark.asyncio
    async def test_get_tx_details_from_solscan(self):
        s = AsyncSolcan()
        await s.init()
        tx_id = "2FM9dAMegHqt75rapiD5Ynpbgd4kT2t7g4QPXhhWLxCXCoGgxgSZwGLDYt3QHXZqDcmNivK7YJ89FXLrS42m2JNS"
        data = await s.get_transaction_details(tx=tx_id)
        assert data["success"] is True
        assert data["data"]["trans_id"] == tx_id

    @pytest.mark.asyncio
    async def test_ensure_inited(self):
        s = AsyncSolcan()
        tx_id = "2FM9dAMegHqt75rapiD5Ynpbgd4kT2t7g4QPXhhWLxCXCoGgxgSZwGLDYt3QHXZqDcmNivK7YJ89FXLrS42m2JNS"
        data = await s.get_transaction_details(tx=tx_id)
        assert data["success"] is True
        assert data["data"]["trans_id"] == tx_id
