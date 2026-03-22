"""Live order service functions for Kiwoom OpenAPI."""

from __future__ import annotations

from typing import Any

from .kiwoom_client import KiwoomClient
from ..constants import APIInfo, ORDER_APIS


def _normalize_return_code(value: Any) -> int | None:
    """Normalize Kiwoom business return codes into integers when possible."""

    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _extract_business_status(response_data: Any) -> tuple[int | None, str | None]:
    """Extract Kiwoom business status from a response payload."""

    if not isinstance(response_data, dict):
        return None, None
    return (
        _normalize_return_code(response_data.get("return_code")),
        response_data.get("return_msg"),
    )


def _build_order_result(
    *,
    api_info: APIInfo,
    context: dict[str, Any],
    result_key: str,
    payload: Any,
    return_code: int | None = None,
    return_msg: str | None = None,
    error: str | None = None,
    status_code: int = 200,
    success_message: str,
) -> dict[str, Any]:
    """Create a normalized result payload for live order requests."""

    success = error is None
    result = {
        "success": success,
        "status_code": status_code,
        "api_id": api_info.api_id,
        "api_name": api_info.name,
        **context,
        result_key: payload,
    }

    if return_code is not None:
        result["return_code"] = return_code
    if return_msg is not None:
        result["return_msg"] = return_msg

    if success:
        result["message"] = return_msg or success_message
    else:
        result["error"] = error
        result["message"] = return_msg or error or "Kiwoom API returned a business error"

    return result


def _build_exception_result(
    *,
    api_info: APIInfo,
    context: dict[str, Any],
    result_key: str,
    message: str,
    error: Exception,
) -> dict[str, Any]:
    """Create a consistent result for transport or runtime errors."""

    return {
        "success": False,
        "status_code": None,
        "api_id": api_info.api_id,
        "api_name": api_info.name,
        **context,
        result_key: None,
        "error": str(error),
        "message": message,
        "note": "This requires proper Kiwoom API endpoint configuration",
    }


async def _submit_order(
    client: KiwoomClient,
    *,
    api_info: APIInfo,
    request_data: dict[str, Any],
    context: dict[str, Any],
    result_key: str,
    success_message: str,
    exception_message: str,
) -> dict[str, Any]:
    """Submit a live order request to Kiwoom and normalize the response."""

    try:
        response = await client.post(
            api_info.url,
            headers={"api-id": api_info.api_id, "cont-yn": "N"},
            json=request_data,
        )
        response_data = response.json()
        return_code, return_msg = _extract_business_status(response_data)

        if return_code not in (None, 0):
            return _build_order_result(
                api_info=api_info,
                context=context,
                result_key=result_key,
                payload=response_data,
                return_code=return_code,
                return_msg=return_msg,
                error=return_msg or f"Kiwoom API returned return_code={return_code}",
                success_message=success_message,
            )

        return _build_order_result(
            api_info=api_info,
            context=context,
            result_key=result_key,
            payload=response_data,
            return_code=return_code,
            return_msg=return_msg,
            success_message=success_message,
        )
    except Exception as error:
        return _build_exception_result(
            api_info=api_info,
            context=context,
            result_key=result_key,
            message=exception_message,
            error=error,
        )


async def place_stock_buy_order(
    client: KiwoomClient,
    stk_cd: str,
    ord_qty: str,
    order_type_code: str,
    ord_uv: str = "",
    cond_uv: str = "",
) -> dict[str, Any]:
    """Submit a live stock buy order to Kiwoom."""

    request_data = {
        "stk_cd": stk_cd,
        "ord_qty": ord_qty,
        "trde_tp": order_type_code,
    }
    if ord_uv:
        request_data["ord_uv"] = ord_uv
    if cond_uv:
        request_data["cond_uv"] = cond_uv

    return await _submit_order(
        client,
        api_info=ORDER_APIS.buy_order,
        request_data=request_data,
        context={
            "stk_cd": stk_cd,
            "ord_qty": ord_qty,
            "order_type_code": order_type_code,
            "ord_uv": ord_uv,
            "cond_uv": cond_uv,
        },
        result_key="buy_order_result",
        success_message="Live stock buy order request submitted",
        exception_message="Stock buy order endpoint not yet implemented or failed to connect",
    )


async def place_stock_sell_order(
    client: KiwoomClient,
    stk_cd: str,
    ord_qty: str,
    order_type_code: str,
    ord_uv: str = "",
    cond_uv: str = "",
) -> dict[str, Any]:
    """Submit a live stock sell order to Kiwoom."""

    request_data = {
        "stk_cd": stk_cd,
        "ord_qty": ord_qty,
        "trde_tp": order_type_code,
    }
    if ord_uv:
        request_data["ord_uv"] = ord_uv
    if cond_uv:
        request_data["cond_uv"] = cond_uv

    return await _submit_order(
        client,
        api_info=ORDER_APIS.sell_order,
        request_data=request_data,
        context={
            "stk_cd": stk_cd,
            "ord_qty": ord_qty,
            "order_type_code": order_type_code,
            "ord_uv": ord_uv,
            "cond_uv": cond_uv,
        },
        result_key="sell_order_result",
        success_message="Live stock sell order request submitted",
        exception_message="Stock sell order endpoint not yet implemented or failed to connect",
    )


async def modify_stock_order(
    client: KiwoomClient,
    orig_ord_no: str,
    stk_cd: str,
    mdfy_qty: str,
    mdfy_uv: str,
    mdfy_cond_uv: str = "",
) -> dict[str, Any]:
    """Submit a live stock modify order to Kiwoom."""

    request_data = {
        "orig_ord_no": orig_ord_no,
        "stk_cd": stk_cd,
        "mdfy_qty": mdfy_qty,
        "mdfy_uv": mdfy_uv,
    }
    if mdfy_cond_uv:
        request_data["mdfy_cond_uv"] = mdfy_cond_uv

    return await _submit_order(
        client,
        api_info=ORDER_APIS.modify_order,
        request_data=request_data,
        context={
            "orig_ord_no": orig_ord_no,
            "stk_cd": stk_cd,
            "mdfy_qty": mdfy_qty,
            "mdfy_uv": mdfy_uv,
            "mdfy_cond_uv": mdfy_cond_uv,
        },
        result_key="modify_order_result",
        success_message="Live stock modify order request submitted",
        exception_message="Stock modify order endpoint not yet implemented or failed to connect",
    )


async def cancel_stock_order(
    client: KiwoomClient,
    orig_ord_no: str,
    stk_cd: str,
    cncl_qty: str,
) -> dict[str, Any]:
    """Submit a live stock cancel order to Kiwoom."""

    return await _submit_order(
        client,
        api_info=ORDER_APIS.cancel_order,
        request_data={
            "orig_ord_no": orig_ord_no,
            "stk_cd": stk_cd,
            "cncl_qty": cncl_qty,
        },
        context={
            "orig_ord_no": orig_ord_no,
            "stk_cd": stk_cd,
            "cncl_qty": cncl_qty,
        },
        result_key="cancel_order_result",
        success_message="Live stock cancel order request submitted",
        exception_message="Stock cancel order endpoint not yet implemented or failed to connect",
    )


__all__ = [
    "place_stock_buy_order",
    "place_stock_sell_order",
    "modify_stock_order",
    "cancel_stock_order",
]
