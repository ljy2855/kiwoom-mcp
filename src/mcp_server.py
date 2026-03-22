"""MCP server implementation using FastMCP for Kiwoom OpenAPI integration."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

from .config import get_settings
from .services.kiwoom_client import KiwoomClient
from .services import account, order

DateYmd = Annotated[
    str,
    Field(description="YYYYMMDD 형식의 날짜. 예: 20260322", pattern=r"^\d{8}$"),
]
StockCode = Annotated[
    str,
    Field(description="6자리 종목코드. 예: 005930", pattern=r"^\d{6}$"),
]
OptionalStockCode = Annotated[
    str | None,
    Field(description="6자리 종목코드. 필요할 때만 입력", pattern=r"^\d{6}$"),
]
NumericText = Annotated[
    str,
    Field(description="숫자만 포함한 문자열", pattern=r"^\d+$"),
]
OptionalNumericText = Annotated[
    str | None,
    Field(description="필요할 때만 입력하는 숫자 문자열", pattern=r"^\d+$"),
]
OrderNumber = Annotated[
    str,
    Field(description="주문번호 또는 원주문번호. 숫자 문자열", pattern=r"^\d+$"),
]
ConfirmLiveOrder = Annotated[
    Literal[True],
    Field(description="실제 주문 실행 확인. 반드시 true여야만 실주문 요청을 전송합니다"),
]
OrderTypeCode = Annotated[
    Literal["0", "3", "5", "61", "62", "81", "6", "7", "10", "13", "16", "20", "23", "26", "28", "29", "30", "31"],
    Field(
        description=(
            "주문구분코드. 예: 0=보통(지정가), 3=시장가, 5=조건부지정가, "
            "61=장시작전시간외, 62=시간외단일가, 81=장마감후시간외"
        )
    ),
]


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
            start_date: DateYmd,
            stock_code: Annotated[
                str | None,
                Field(
                    description="호환성용 종목코드. 현재 REST API는 start_date 기준으로 조회하며 이 값이 실질적으로 사용되지 않을 수 있음",
                    pattern=r"^\d{6}$",
                ),
            ] = None,
        ) -> dict[str, Any]:
            """
            API `ka10072` 일자별종목별실현손익요청_일자.

            특정 시작일 이후의 실현손익 내역을 조회합니다.
            현재 Kiwoom REST 응답은 `start_date` 기준 조회가 핵심이며, `stock_code`는 기존 인터페이스 호환용입니다.

            Use this tool when:
            - 계좌의 일자별/종목별 실현손익이 있는지 확인하고 싶을 때
            - 결과가 0건이어도 정상 응답인지 구분하고 싶을 때
            """
            return await account.get_daily_realized_profit_by_stock(
                self._client, stock_code or "", start_date
            )

        @self.mcp.tool()
        async def get_account_evaluation(
            qry_tp: Annotated[
                Literal["0", "1"],
                Field(description="상장폐지조회구분. 0=전체, 1=상장폐지종목 제외"),
            ] = "0",
            dmst_stex_tp: Annotated[
                Literal["KRX", "NXT"],
                Field(description="국내거래소구분. 일반적으로 KRX 사용"),
            ] = "KRX",
        ) -> dict[str, Any]:
            """
            API `kt00004` 계좌평가현황요청.

            보유 종목 평가금액, 손익, 예수금 추정자산 등을 조회합니다.
            기본값은 대부분의 경우 그대로 사용하면 됩니다.
            """
            return await account.get_account_evaluation(
                self._client, qry_tp, dmst_stex_tp
            )

        @self.mcp.tool()
        async def get_account_current_status(
        ) -> dict[str, Any]:
            """
            API `kt00017` 계좌별당일현황요청.

            추가 인자 없이 당일 계좌 현황을 조회합니다.
            D+2 추정예수금, 일반주식평가금액, 수수료/세금 등의 스냅샷이 필요할 때 사용합니다.
            """
            return await account.get_account_current_status(
                self._client
            )

        @self.mcp.tool()
        async def get_daily_account_profit_detail(
            fr_dt: DateYmd,
            to_dt: DateYmd,
        ) -> dict[str, Any]:
            """
            API `kt00016` 일별계좌수익률상세현황요청.

            기간별 계좌 수익률과 예수금/평가금액 변화를 조회합니다.
            `fr_dt`, `to_dt`는 반드시 YYYYMMDD 형식이어야 합니다.
            """
            return await account.get_daily_account_profit_detail(
                self._client, fr_dt, to_dt
            )

        @self.mcp.tool()
        async def get_orderable_amount(
            stk_cd: StockCode,
            trde_tp: Annotated[
                Literal["1", "2"],
                Field(description="매매구분. 1=매도, 2=매수"),
            ],
            uv: NumericText,
            trde_qty: OptionalNumericText = None,
            exp_buy_unp: OptionalNumericText = None,
        ) -> dict[str, Any]:
            """
            API `kt00010` 주문인출가능금액요청.

            특정 종목을 기준으로 주문 가능 금액/수량을 조회합니다.

            Important:
            - `uv`는 주문 단가를 숫자 문자열로 넣어야 합니다. 예: `"70000"`
            - 장이 닫혀 있으면 `success=false`와 함께 업무 오류 메시지가 반환될 수 있습니다
            """
            return await account.get_orderable_amount(
                self._client,
                stk_cd,
                trde_tp,
                uv,
                trde_qty=trde_qty or "",
                exp_buy_unp=exp_buy_unp or "",
            )

        @self.mcp.tool()
        async def get_execution_info(
            qry_tp: Annotated[
                Literal["0", "1"],
                Field(description="조회구분. 0=전체, 1=종목"),
            ],
            sell_tp: Annotated[
                Literal["0", "1", "2"],
                Field(description="매도수구분. 0=전체, 1=매도, 2=매수"),
            ],
            stex_tp: Annotated[
                Literal["0", "1", "2"],
                Field(description="거래소구분. 0=통합, 1=KRX, 2=NXT"),
            ],
            stk_cd: OptionalStockCode = None,
            ord_no: OptionalNumericText = None,
        ) -> dict[str, Any]:
            """
            API `ka10076` 체결요청.

            체결이 완료된 주문 내역만 조회합니다.

            Use this tool when:
            - 실제 체결된 주문 목록이 필요할 때
            - 미체결/접수 상태가 아니라 체결 결과만 보고 싶을 때

            If you need:
            - 주문/접수/확인/체결 현황 전체 스냅샷: use `get_order_execution_status`
            """
            return await account.get_execution_info(
                self._client,
                qry_tp,
                sell_tp,
                stex_tp,
                stk_cd or "",
                ord_no or "",
            )

        @self.mcp.tool()
        async def get_order_execution_status(
            stk_bond_tp: Annotated[
                Literal["0", "1", "2"],
                Field(description="주식채권구분. 0=전체, 1=주식, 2=채권"),
            ],
            mrkt_tp: Annotated[
                Literal["0", "1", "2", "3", "4"],
                Field(description="시장구분. 0=전체, 1=코스피, 2=코스닥, 3=OTCBB, 4=ECN"),
            ],
            sell_tp: Annotated[
                Literal["0", "1", "2"],
                Field(description="매도수구분. 0=전체, 1=매도, 2=매수"),
            ],
            qry_tp: Annotated[
                Literal["0", "1"],
                Field(description="조회구분. 0=전체, 1=체결"),
            ],
            dmst_stex_tp: Annotated[
                Literal["%", "KRX", "NXT", "SOR"],
                Field(description="국내거래소구분. %=전체, KRX=한국거래소, NXT=넥스트트레이드, SOR=최선집행"),
            ],
            stk_cd: OptionalStockCode = None,
            fr_ord_no: OptionalNumericText = None,
        ) -> dict[str, Any]:
            """
            API `kt00009` 계좌별주문체결현황요청.

            주문/접수/확인/체결 상태를 함께 보는 계좌별 주문 현황 조회입니다.
            `get_execution_info`와 다르게 체결 완료 내역만 보는 도구가 아닙니다.

            Use this tool when:
            - 주문 현황 전체 스냅샷이 필요할 때
            - 특정 주문번호 이후의 진행 상태를 이어서 조회할 때
            """
            return await account.get_order_execution_status(
                self._client,
                stk_bond_tp,
                mrkt_tp,
                sell_tp,
                qry_tp,
                dmst_stex_tp,
                stk_cd or "",
                fr_ord_no or "",
            )

        @self.mcp.tool()
        async def get_unexecuted_orders(
            all_stk_tp: Annotated[
                Literal["0", "1"],
                Field(description="전체종목구분. 0=전체, 1=종목"),
            ],
            trde_tp: Annotated[
                Literal["0", "1", "2"],
                Field(description="매매구분. 0=전체, 1=매도, 2=매수"),
            ],
            stex_tp: Annotated[
                Literal["0", "1", "2"],
                Field(description="거래소구분. 0=통합, 1=KRX, 2=NXT"),
            ],
            stk_cd: OptionalStockCode = None,
        ) -> dict[str, Any]:
            """
            API `ka10075` 미체결요청.

            현재 미체결 주문만 조회합니다.

            Important:
            - `all_stk_tp`는 실제 서버가 요구하는 필수값입니다
            - 결과가 0건이면 미체결 주문이 없다는 뜻일 수 있습니다
            """
            return await account.get_unexecuted_orders(
                self._client, all_stk_tp, trde_tp, stex_tp, stk_cd or ""
            )

        @self.mcp.tool()
        async def place_stock_buy_order(
            confirm_live_order: ConfirmLiveOrder,
            stk_cd: StockCode,
            ord_qty: NumericText,
            order_type_code: OrderTypeCode,
            ord_uv: OptionalNumericText = None,
            cond_uv: OptionalNumericText = None,
        ) -> dict[str, Any]:
            """
            LIVE ORDER: API `kt10000` 주식 매수주문.

            실제 매수 주문을 전송합니다. 시뮬레이션용이 아닙니다.

            Important:
            - 이 도구는 실거래 주문을 발생시킵니다
            - `confirm_live_order`는 반드시 `true`여야 합니다
            - 시장가 주문이면 `order_type_code="3"`를 사용하고 `ord_uv`는 비워둘 수 있습니다
            - 지정가 주문이면 `order_type_code="0"`와 `ord_uv`를 함께 넣으세요
            """
            return await order.place_stock_buy_order(
                self._client,
                stk_cd=stk_cd,
                ord_qty=ord_qty,
                order_type_code=order_type_code,
                ord_uv=ord_uv or "",
                cond_uv=cond_uv or "",
            )

        @self.mcp.tool()
        async def place_stock_sell_order(
            confirm_live_order: ConfirmLiveOrder,
            stk_cd: StockCode,
            ord_qty: NumericText,
            order_type_code: OrderTypeCode,
            ord_uv: OptionalNumericText = None,
            cond_uv: OptionalNumericText = None,
        ) -> dict[str, Any]:
            """
            LIVE ORDER: API `kt10001` 주식 매도주문.

            실제 매도 주문을 전송합니다. 시뮬레이션용이 아닙니다.

            Important:
            - 이 도구는 실거래 주문을 발생시킵니다
            - `confirm_live_order`는 반드시 `true`여야 합니다
            - 시장가 주문이면 `order_type_code="3"`를 사용하고 `ord_uv`는 비워둘 수 있습니다
            - 지정가 주문이면 `order_type_code="0"`와 `ord_uv`를 함께 넣으세요
            """
            return await order.place_stock_sell_order(
                self._client,
                stk_cd=stk_cd,
                ord_qty=ord_qty,
                order_type_code=order_type_code,
                ord_uv=ord_uv or "",
                cond_uv=cond_uv or "",
            )

        @self.mcp.tool()
        async def modify_stock_order(
            confirm_live_order: ConfirmLiveOrder,
            orig_ord_no: OrderNumber,
            stk_cd: StockCode,
            mdfy_qty: NumericText,
            mdfy_uv: NumericText,
            mdfy_cond_uv: OptionalNumericText = None,
        ) -> dict[str, Any]:
            """
            LIVE ORDER: API `kt10002` 주식 정정주문.

            기존 주문을 정정합니다. 실주문 변경이므로 주의해서 사용해야 합니다.
            """
            return await order.modify_stock_order(
                self._client,
                orig_ord_no=orig_ord_no,
                stk_cd=stk_cd,
                mdfy_qty=mdfy_qty,
                mdfy_uv=mdfy_uv,
                mdfy_cond_uv=mdfy_cond_uv or "",
            )

        @self.mcp.tool()
        async def cancel_stock_order(
            confirm_live_order: ConfirmLiveOrder,
            orig_ord_no: OrderNumber,
            stk_cd: StockCode,
            cncl_qty: NumericText,
        ) -> dict[str, Any]:
            """
            LIVE ORDER: API `kt10003` 주식 취소주문.

            기존 주문을 취소합니다. `cncl_qty="0"`이면 잔량 전체 취소입니다.
            """
            return await order.cancel_stock_order(
                self._client,
                orig_ord_no=orig_ord_no,
                stk_cd=stk_cd,
                cncl_qty=cncl_qty,
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
