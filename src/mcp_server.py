"""MCP server implementation using FastMCP for Kiwoom OpenAPI integration."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

from fastmcp import FastMCP

from .config import Settings, get_settings
from .services.kiwoom_client import KiwoomClient
from .services import account


class KiwoomMCPServer:
    """MCP server that provides Kiwoom OpenAPI functionality."""

    def __init__(self):
        self.mcp = FastMCP("kiwoom-mcp")
        self._client = KiwoomClient(get_settings())
        self._setup_resources()
        self._setup_tools()

    def _setup_resources(self) -> None:
        """Setup MCP resources for configuration and status."""
        

    def _setup_tools(self) -> None:
        """Setup MCP tools for Kiwoom OpenAPI operations."""
        
        @self.mcp.tool()
        async def get_daily_realized_profit_by_stock(
            stock_code: str,
            start_date: str,
        ) -> Dict[str, Any]:
            """
            Get daily realized profit/loss by stock for a specific date with automatic pagination.
            Automatically fetches all available data by handling continuous inquiry.
            
            Args:
                stock_code: Stock code (6 digits, e.g., "005930" for Samsung Electronics)
                start_date: Start date in YYYYMMDD format (e.g., "20241128")
                
            Returns:
                Complete daily realized profit/loss information by stock including:
                - Stock name, contract quantity, purchase price, contract price
                - Daily selling profit/loss, profit/loss ratio
                - Trading commission, trading tax, withdrawable amount
                - Total records count and request count for pagination info
            """
            return await account.get_daily_realized_profit_by_stock(
                self._client, stock_code, start_date
            )

        @self.mcp.tool()
        async def get_account_evaluation(
            qry_tp: str = "0",
            dmst_stex_tp: str = "KRX",
        ) -> Dict[str, Any]:
            """
            Get account evaluation status with automatic pagination.
            Automatically fetches all available data by handling continuous inquiry.
            
            Args:
                qry_tp: 상장폐지조회구분 (0: 전체, 1: 상장폐지종목제외, default: "0")
                dmst_stex_tp: 국내거래소구분 (KRX: 한국거래소, NXT: 넥스트트레이드, default: "KRX")
                
            Returns:
                Complete account evaluation information including:
                - Account balance, asset value, profit/loss
                - Stock holdings and their current values
                - Total evaluation amount and profit/loss ratio
                - Total records count and request count for pagination info
            """
            return await account.get_account_evaluation(
                self._client, qry_tp, dmst_stex_tp
            )

        @self.mcp.tool()
        async def get_account_current_status(
        ) -> Dict[str, Any]:
            """
            Get account current status with automatic pagination.
            Automatically fetches all available data by handling continuous inquiry.
            
            Args:
                
            Returns:
                Complete account current status information including:
                - D+2 추정예수금, 신용이자미납금, 기타대여금
                - 일반주식평가금액, 예탁담보대출금, 신용융자금
                - 입출금 현황, 매매 현황, 수수료 및 세금
                - RP/채권/ELS 평가금액, 배당금액
                - Total records count and request count for pagination info
            """
            return await account.get_account_current_status(
                self._client
            )

        @self.mcp.tool()
        async def get_daily_account_profit_detail(
            fr_dt: str,
            to_dt: str,
        ) -> Dict[str, Any]:
            """
            Get daily account profit rate detailed status with automatic pagination.
            Automatically fetches all available data by handling continuous inquiry.
            
            Args:
                fr_dt: 평가시작일 in YYYYMMDD format (e.g., "20241111")
                to_dt: 평가종료일 in YYYYMMDD format (e.g., "20241125")
                
            Returns:
                Complete daily account profit rate detailed status including:
                - 관리사원번호, 관리자명, 관리자지점
                - 예수금 초/말, 유가증권평가금액 초/말
                - 대주담보금 초/말, 신용융자금 초/말
                - 현금미수금 초/말, 원화대용금 초/말
                - 투자원금평잔, 평가손익, 수익률, 회전율
                - 기간내 총입금/출금, 총입고/출고
                - 선물대용매도금액, 위탁대용매도금액
                - Total records count and request count for pagination info
            """
            return await account.get_daily_account_profit_detail(
                self._client, fr_dt, to_dt
            )

        @self.mcp.tool()
        async def get_orderable_amount(
            stk_cd: str,
            trde_tp: str,
            uv: str,
            io_amt: str = "",
            trde_qty: str = "",
            exp_buy_unp: str = ""
        ) -> Dict[str, Any]:
            """
            Get orderable/withdrawable amount with automatic pagination.
            Automatically fetches all available data by handling continuous inquiry.
            
            Args:
                stk_cd: 종목번호 (Stock Code, e.g., "005930")
                trde_tp: 매매구분 (Trade Type: "1"=매도, "2"=매수)
                uv: 매수가격 (Purchase Price)
                io_amt: 입출금액 (Deposit/Withdrawal Amount, optional)
                trde_qty: 매매수량 (Trade Quantity, optional)
                exp_buy_unp: 예상매수단가 (Expected Purchase Unit Price, optional)
                
            Returns:
                Complete orderable/withdrawable amount information including:
                - 증거금별 주문가능금액/수량 (20%, 30%, 40%, 50%, 60%, 100%)
                - 증거금감면60% 주문가능금액/수량
                - 전일/금일 재사용가능금액
                - 예수금, 대용금, 미수금
                - 주문가능대용, 주문가능현금
                - 인출가능금액, 익일인출가능금액
                - 매입금액, 수수료, 매입정산금
                - D+2추정예수금, 증거금감면적용구분
                - Total records count and request count for pagination info
            """
            return await account.get_orderable_amount(
                self._client, stk_cd, trde_tp, uv, io_amt, trde_qty, exp_buy_unp
            )

        @self.mcp.tool()
        async def get_execution_info(
            qry_tp: str,
            sell_tp: str,
            stex_tp: str,
            stk_cd: str = "",
            ord_no: str = ""
        ) -> Dict[str, Any]:
            """
            Get execution information with automatic pagination.
            Automatically fetches all available data by handling continuous inquiry.
            
            Args:
                qry_tp: 조회구분 (Inquiry Type: "0"=전체, "1"=종목)
                sell_tp: 매도수구분 (Buy/Sell Type: "0"=전체, "1"=매도, "2"=매수)
                stex_tp: 거래소구분 (Exchange Type: "0"=통합, "1"=KRX, "2"=NXT)
                stk_cd: 종목코드 (Stock Code, optional, e.g., "005930")
                ord_no: 주문번호 (Order Number, optional, for search criterion)
                
            Returns:
                Complete execution information including:
                - 주문번호, 종목명, 주문구분
                - 주문가격, 주문수량, 체결가, 체결량
                - 미체결수량, 당일매매수수료, 당일매매세금
                - 주문상태, 매매구분, 원주문번호
                - 주문시간, 종목코드, 거래소구분
                - SOR 여부값, 스톱가
                - Total records count and request count for pagination info
            """
            return await account.get_execution_info(
                self._client, qry_tp, sell_tp, stex_tp, stk_cd, ord_no
            )

        @self.mcp.tool()
        async def get_unexecuted_orders(
            all_stk_tp: str,
            trde_tp: str,
            stex_tp: str,
            stk_cd: str = ""
        ) -> Dict[str, Any]:
            """
            Get unexecuted orders with automatic pagination.
            Automatically fetches all available data by handling continuous inquiry.
            
            Args:
                all_stk_tp: 전체종목구분 (All Stock Type: "0"=전체, "1"=종목)
                trde_tp: 매매구분 (Trade Type: "0"=전체, "1"=매도, "2"=매수)
                stex_tp: 거래소구분 (Exchange Type: "0"=통합, "1"=KRX, "2"=NXT)
                stk_cd: 종목코드 (Stock Code, optional, e.g., "005930")
                
            Returns:
                Complete unexecuted orders information including:
                - 계좌번호, 주문번호, 관리사번
                - 종목코드, 업무구분, 주문상태, 종목명
                - 주문수량, 주문가격, 미체결수량
                - 체결누계금액, 원주문번호, 주문구분
                - 매매구분, 시간, 체결번호
                - 체결가, 체결량, 현재가
                - 매도호가, 매수호가, 단위체결가/량
                - 당일매매수수료, 당일매매세금
                - 개인투자자, 거래소구분, SOR 여부값, 스톱가
                - Total records count and request count for pagination info
            """
            return await account.get_unexecuted_orders(
                self._client, all_stk_tp, trde_tp, stex_tp, stk_cd
            )


    async def close(self) -> None:
        """Close the HTTP client connection."""
        await self._client.close()

    def run(self) -> None:
        """Run the MCP server."""
        self.mcp.run()


# Create global server instance
mcp_server = KiwoomMCPServer()


def create_mcp_server() -> KiwoomMCPServer:
    """Create and return a new MCP server instance."""
    return KiwoomMCPServer()


__all__ = ["KiwoomMCPServer", "mcp_server", "create_mcp_server"]
