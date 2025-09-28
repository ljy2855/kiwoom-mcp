"""Account-related service functions for Kiwoom OpenAPI."""

from typing import Dict, Any
from .kiwoom_client import KiwoomClient
from ..constants import ACCOUNT_APIS


async def get_daily_realized_profit_by_stock(
    client: KiwoomClient, 
    stock_code: str, 
    start_date: str,
    max_requests: int = 10
) -> Dict[str, Any]:
    """
    Get daily realized profit/loss by stock for a specific date with automatic pagination.
    Automatically handles continuous inquiry to fetch all available data.
    
    Args:
        client: KiwoomClient instance
        stock_code: Stock code (6 digits, e.g., "005930")
        start_date: Start date in YYYYMMDD format
        max_requests: Maximum number of API requests to prevent infinite loops (default: 10)
        
    Returns:
        Complete daily realized profit/loss information by stock with all paginated data
    """
    try:
        # Use the actual Kiwoom API for daily realized profit by stock
        api_info = ACCOUNT_APIS["DAILY_REALIZED_PROFIT_BY_STOCK"]
        
        all_data = []
        cont_yn = "N"
        next_key = None
        request_count = 0
        
        while request_count < max_requests:
            # Prepare request data
            request_data = {
                "stk_cd": stock_code,
                "strt_dt": start_date
            }
            
            # Prepare headers
            headers = {
                "api-id": api_info.api_id,
                "cont-yn": cont_yn
            }
            
            if next_key:
                headers["next-key"] = next_key
            
            # Make API request
            response = await client.post(api_info.url, json=request_data, headers=headers)
            request_count += 1
            
            if response.status_code != 200:
                return {
                    "status_code": response.status_code,
                    "api_id": api_info.api_id,
                    "api_name": api_info.name,
                    "stock_code": stock_code,
                    "start_date": start_date,
                    "error": f"API request failed with status {response.status_code}",
                    "message": "Failed to retrieve daily realized profit by stock"
                }
            
            # Parse response
            response_data = response.json()
            
            # Extract data from response
            if "dt_stk_div_rlzt_pl" in response_data:
                batch_data = response_data["dt_stk_div_rlzt_pl"]
                if batch_data:
                    all_data.extend(batch_data)
            
            # Check if there's more data to fetch
            response_cont_yn = response.headers.get("cont-yn", "N")
            response_next_key = response.headers.get("next-key")
            
            if response_cont_yn == "Y" and response_next_key:
                cont_yn = "Y"
                next_key = response_next_key
            else:
                # No more data to fetch
                break
        
        # Prepare final result
        result = {
            "status_code": 200,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "stock_code": stock_code,
            "start_date": start_date,
            "total_requests": request_count,
            "total_records": len(all_data),
            "realized_profit_data": all_data,
            "message": f"Successfully retrieved {len(all_data)} records in {request_count} requests"
        }
        
        # Add warning if we hit the max requests limit
        if request_count >= max_requests:
            result["warning"] = f"Reached maximum request limit ({max_requests}). There may be more data available."
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Daily realized profit by stock endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_account_evaluation(
    client: KiwoomClient, 
    qry_tp: str = "0",
    dmst_stex_tp: str = "KRX",
    max_requests: int = 10
) -> Dict[str, Any]:
    """
    Get account evaluation status with automatic pagination.
    Automatically handles continuous inquiry to fetch all available data.
    
    Args:
        client: KiwoomClient instance
        qry_tp: 상장폐지조회구분 (0: 전체, 1: 상장폐지종목제외, default: "0")
        dmst_stex_tp: 국내거래소구분 (KRX: 한국거래소, NXT: 넥스트트레이드, default: "KRX")
        max_requests: Maximum number of API requests to prevent infinite loops (default: 10)
        
    Returns:
        Complete account evaluation information with all paginated data
    """
    try:
        # Use the actual Kiwoom API for account evaluation
        api_info = ACCOUNT_APIS["ACCOUNT_EVALUATION"]
        
        all_data = []
        cont_yn = "N"
        next_key = None
        request_count = 0
        
        while request_count < max_requests:
            # Prepare request data according to API spec
            request_data = {
                "qry_tp": qry_tp,
                "dmst_stex_tp": dmst_stex_tp
            }
            
            # Prepare headers
            headers = {
                "api-id": api_info.api_id,
                "cont-yn": cont_yn
            }
            
            if next_key:
                headers["next-key"] = next_key
            
            # Make API request
            response = await client.post(api_info.url, json=request_data, headers=headers)
            request_count += 1
            
            if response.status_code != 200:
                return {
                    "status_code": response.status_code,
                    "api_id": api_info.api_id,
                    "api_name": api_info.name,
                    "qry_tp": qry_tp,
                    "dmst_stex_tp": dmst_stex_tp,
                    "error": f"API request failed with status {response.status_code}",
                    "message": "Failed to retrieve account evaluation"
                }
            
            # Parse response
            response_data = response.json()
            
            # Extract data from response - account evaluation returns account data
            if "stk_acnt_evit_prst" in response_data:
                batch_data = response_data["stk_acnt_evit_prst"]
                if batch_data:
                    all_data.extend(batch_data)
            elif isinstance(response_data, list):
                all_data.extend(response_data)
            elif isinstance(response_data, dict) and response_data:
                all_data.append(response_data)
            
            # Check if there's more data to fetch
            response_cont_yn = response.headers.get("cont-yn", "N")
            response_next_key = response.headers.get("next-key")
            
            if response_cont_yn == "Y" and response_next_key:
                cont_yn = "Y"
                next_key = response_next_key
            else:
                # No more data to fetch
                break
        
        # Prepare final result
        result = {
            "status_code": 200,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "qry_tp": qry_tp,
            "dmst_stex_tp": dmst_stex_tp,
            "total_requests": request_count,
            "total_records": len(all_data),
            "evaluation_data": all_data,
            "message": f"Successfully retrieved {len(all_data)} records in {request_count} requests"
        }
        
        # Add warning if we hit the max requests limit
        if request_count >= max_requests:
            result["warning"] = f"Reached maximum request limit ({max_requests}). There may be more data available."
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Account evaluation endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_account_current_status(
    client: KiwoomClient, 
    max_requests: int = 10
) -> Dict[str, Any]:
    """
    Get account daily status with automatic pagination.
    Automatically handles continuous inquiry to fetch all available data.
    
    Args:
        client: KiwoomClient instance
        max_requests: Maximum number of API requests to prevent infinite loops (default: 10)
        
    Returns:
        Complete account daily status information with all paginated data including:
        - D+2 추정예수금, 신용이자미납금, 기타대여금
        - 일반주식평가금액, 예탁담보대출금, 신용융자금
        - 입출금 현황, 매매 현황, 수수료 및 세금
        - RP/채권/ELS 평가금액, 배당금액 등
    """
    try:
        # Use the actual Kiwoom API for account daily status
        api_info = ACCOUNT_APIS["ACCOUNT_DAILY_STATUS"]
        
        all_data = []
        cont_yn = "N"
        next_key = None
        request_count = 0
        
        while request_count < max_requests:
            # Prepare request data - no body parameters required for this API
            request_data = {}
            
            # Prepare headers
            headers = {
                "api-id": api_info.api_id,
                "cont-yn": cont_yn
            }
            
            if next_key:
                headers["next-key"] = next_key
            
            # Make API request
            response = await client.post(api_info.url, json=request_data, headers=headers)
            request_count += 1
            
            if response.status_code != 200:
                return {
                    "status_code": response.status_code,
                    "api_id": api_info.api_id,
                    "api_name": api_info.name,
                    "error": f"API request failed with status {response.status_code}",
                    "message": "Failed to retrieve account daily status"
                }
            
            # Parse response
            response_data = response.json()
            
            # Extract data from response - account daily status returns account data
            if isinstance(response_data, list):
                all_data.extend(response_data)
            elif isinstance(response_data, dict) and response_data:
                all_data.append(response_data)
            
            # Check if there's more data to fetch
            response_cont_yn = response.headers.get("cont-yn", "N")
            response_next_key = response.headers.get("next-key")
            
            if response_cont_yn == "Y" and response_next_key:
                cont_yn = "Y"
                next_key = response_next_key
            else:
                # No more data to fetch
                break
        
        # Prepare final result
        result = {
            "status_code": 200,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "total_requests": request_count,
            "total_records": len(all_data),
            "daily_status_data": all_data,
            "message": f"Successfully retrieved {len(all_data)} records in {request_count} requests"
        }
        
        # Add warning if we hit the max requests limit
        if request_count >= max_requests:
            result["warning"] = f"Reached maximum request limit ({max_requests}). There may be more data available."
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Account daily status endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_daily_account_profit_detail(
    client: KiwoomClient, 
    fr_dt: str,
    to_dt: str,
    max_requests: int = 10
) -> Dict[str, Any]:
    """
    Get daily account profit rate detailed status with automatic pagination.
    Automatically handles continuous inquiry to fetch all available data.
    
    Args:
        client: KiwoomClient instance
        fr_dt: 평가시작일 in YYYYMMDD format (e.g., "20241111")
        to_dt: 평가종료일 in YYYYMMDD format (e.g., "20241125")
        max_requests: Maximum number of API requests to prevent infinite loops (default: 10)
        
    Returns:
        Complete daily account profit rate detailed status with all paginated data including:
        - 관리사원번호, 관리자명, 관리자지점
        - 예수금 초/말, 유가증권평가금액 초/말
        - 대주담보금 초/말, 신용융자금 초/말
        - 현금미수금 초/말, 원화대용금 초/말
        - 투자원금평잔, 평가손익, 수익률, 회전율
        - 기간내 총입금/출금, 총입고/출고
        - 선물대용매도금액, 위탁대용매도금액 등
    """
    try:
        # Use the actual Kiwoom API for daily account profit detail
        api_info = ACCOUNT_APIS["DAILY_ACCOUNT_PROFIT_DETAIL"]
        
        all_data = []
        cont_yn = "N"
        next_key = None
        request_count = 0
        
        while request_count < max_requests:
            # Prepare request data according to API spec
            request_data = {
                "fr_dt": fr_dt,
                "to_dt": to_dt
            }
            
            # Prepare headers
            headers = {
                "api-id": api_info.api_id,
                "cont-yn": cont_yn
            }
            
            if next_key:
                headers["next-key"] = next_key
            
            # Make API request
            response = await client.post(api_info.url, json=request_data, headers=headers)
            request_count += 1
            
            if response.status_code != 200:
                return {
                    "status_code": response.status_code,
                    "api_id": api_info.api_id,
                    "api_name": api_info.name,
                    "fr_dt": fr_dt,
                    "to_dt": to_dt,
                    "error": f"API request failed with status {response.status_code}",
                    "message": "Failed to retrieve daily account profit detail"
                }
            
            # Parse response
            response_data = response.json()
            
            # Extract data from response - daily account profit detail returns account data
            if isinstance(response_data, list):
                all_data.extend(response_data)
            elif isinstance(response_data, dict) and response_data:
                all_data.append(response_data)
            
            # Check if there's more data to fetch
            response_cont_yn = response.headers.get("cont-yn", "N")
            response_next_key = response.headers.get("next-key")
            
            if response_cont_yn == "Y" and response_next_key:
                cont_yn = "Y"
                next_key = response_next_key
            else:
                # No more data to fetch
                break
        
        # Prepare final result
        result = {
            "status_code": 200,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "fr_dt": fr_dt,
            "to_dt": to_dt,
            "total_requests": request_count,
            "total_records": len(all_data),
            "profit_detail_data": all_data,
            "message": f"Successfully retrieved {len(all_data)} records in {request_count} requests"
        }
        
        # Add warning if we hit the max requests limit
        if request_count >= max_requests:
            result["warning"] = f"Reached maximum request limit ({max_requests}). There may be more data available."
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Daily account profit detail endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_orderable_amount(
    client: KiwoomClient, 
    stk_cd: str,
    trde_tp: str,
    uv: str,
    io_amt: str = "",
    trde_qty: str = "",
    exp_buy_unp: str = "",
    max_requests: int = 10
) -> Dict[str, Any]:
    """
    Get orderable/withdrawable amount with automatic pagination.
    Automatically handles continuous inquiry to fetch all available data.
    
    Args:
        client: KiwoomClient instance
        stk_cd: 종목번호 (Stock Code, e.g., "005930")
        trde_tp: 매매구분 (Trade Type: "1"=매도, "2"=매수)
        uv: 매수가격 (Purchase Price)
        io_amt: 입출금액 (Deposit/Withdrawal Amount, optional)
        trde_qty: 매매수량 (Trade Quantity, optional)
        exp_buy_unp: 예상매수단가 (Expected Purchase Unit Price, optional)
        max_requests: Maximum number of API requests to prevent infinite loops (default: 10)
        
    Returns:
        Complete orderable/withdrawable amount information with all paginated data including:
        - 증거금별 주문가능금액/수량 (20%, 30%, 40%, 50%, 60%, 100%)
        - 증거금감면60% 주문가능금액/수량
        - 전일/금일 재사용가능금액
        - 예수금, 대용금, 미수금
        - 주문가능대용, 주문가능현금
        - 인출가능금액, 익일인출가능금액
        - 매입금액, 수수료, 매입정산금
        - D+2추정예수금, 증거금감면적용구분
    """
    try:
        # Use the actual Kiwoom API for orderable amount
        api_info = ACCOUNT_APIS["ORDERABLE_AMOUNT"]
        
        all_data = []
        cont_yn = "N"
        next_key = None
        request_count = 0
        
        while request_count < max_requests:
            # Prepare request data according to API spec
            request_data = {
                "stk_cd": stk_cd,
                "trde_tp": trde_tp,
                "uv": uv
            }
            
            # Add optional parameters if provided
            if io_amt:
                request_data["io_amt"] = io_amt
            if trde_qty:
                request_data["trde_qty"] = trde_qty
            if exp_buy_unp:
                request_data["exp_buy_unp"] = exp_buy_unp
            
            # Prepare headers
            headers = {
                "api-id": api_info.api_id,
                "cont-yn": cont_yn
            }
            
            if next_key:
                headers["next-key"] = next_key
            
            # Make API request
            response = await client.post(api_info.url, json=request_data, headers=headers)
            request_count += 1
            
            if response.status_code != 200:
                return {
                    "status_code": response.status_code,
                    "api_id": api_info.api_id,
                    "api_name": api_info.name,
                    "stk_cd": stk_cd,
                    "trde_tp": trde_tp,
                    "uv": uv,
                    "error": f"API request failed with status {response.status_code}",
                    "message": "Failed to retrieve orderable amount"
                }
            
            # Parse response
            response_data = response.json()
            
            # Extract data from response - orderable amount returns account data
            if isinstance(response_data, list):
                all_data.extend(response_data)
            elif isinstance(response_data, dict) and response_data:
                all_data.append(response_data)
            
            # Check if there's more data to fetch
            response_cont_yn = response.headers.get("cont-yn", "N")
            response_next_key = response.headers.get("next-key")
            
            if response_cont_yn == "Y" and response_next_key:
                cont_yn = "Y"
                next_key = response_next_key
            else:
                # No more data to fetch
                break
        
        # Prepare final result
        result = {
            "status_code": 200,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "stk_cd": stk_cd,
            "trde_tp": trde_tp,
            "uv": uv,
            "total_requests": request_count,
            "total_records": len(all_data),
            "orderable_amount_data": all_data,
            "message": f"Successfully retrieved {len(all_data)} records in {request_count} requests"
        }
        
        # Add warning if we hit the max requests limit
        if request_count >= max_requests:
            result["warning"] = f"Reached maximum request limit ({max_requests}). There may be more data available."
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Orderable amount endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_execution_info(
    client: KiwoomClient, 
    qry_tp: str,
    sell_tp: str,
    stex_tp: str,
    stk_cd: str = "",
    ord_no: str = "",
    max_requests: int = 10
) -> Dict[str, Any]:
    """
    Get execution information with automatic pagination.
    Automatically handles continuous inquiry to fetch all available data.
    
    Args:
        client: KiwoomClient instance
        qry_tp: 조회구분 (Inquiry Type: "0"=전체, "1"=종목)
        sell_tp: 매도수구분 (Buy/Sell Type: "0"=전체, "1"=매도, "2"=매수)
        stex_tp: 거래소구분 (Exchange Type: "0"=통합, "1"=KRX, "2"=NXT)
        stk_cd: 종목코드 (Stock Code, optional, e.g., "005930")
        ord_no: 주문번호 (Order Number, optional, for search criterion)
        max_requests: Maximum number of API requests to prevent infinite loops (default: 10)
        
    Returns:
        Complete execution information with all paginated data including:
        - 주문번호, 종목명, 주문구분
        - 주문가격, 주문수량, 체결가, 체결량
        - 미체결수량, 당일매매수수료, 당일매매세금
        - 주문상태, 매매구분, 원주문번호
        - 주문시간, 종목코드, 거래소구분
        - SOR 여부값, 스톱가 등
    """
    try:
        # Use the actual Kiwoom API for execution info
        api_info = ACCOUNT_APIS["EXECUTION_INFO"]
        
        all_data = []
        cont_yn = "N"
        next_key = None
        request_count = 0
        
        while request_count < max_requests:
            # Prepare request data according to API spec
            request_data = {
                "qry_tp": qry_tp,
                "sell_tp": sell_tp,
                "stex_tp": stex_tp
            }
            
            # Add optional parameters if provided
            if stk_cd:
                request_data["stk_cd"] = stk_cd
            if ord_no:
                request_data["ord_no"] = ord_no
            
            # Prepare headers
            headers = {
                "api-id": api_info.api_id,
                "cont-yn": cont_yn
            }
            
            if next_key:
                headers["next-key"] = next_key
            
            # Make API request
            response = await client.post(api_info.url, json=request_data, headers=headers)
            request_count += 1
            
            if response.status_code != 200:
                return {
                    "status_code": response.status_code,
                    "api_id": api_info.api_id,
                    "api_name": api_info.name,
                    "qry_tp": qry_tp,
                    "sell_tp": sell_tp,
                    "stex_tp": stex_tp,
                    "stk_cd": stk_cd,
                    "ord_no": ord_no,
                    "error": f"API request failed with status {response.status_code}",
                    "message": "Failed to retrieve execution info"
                }
            
            # Parse response
            response_data = response.json()
            
            # Extract data from response - execution info returns execution data
            if "cntr" in response_data:
                batch_data = response_data["cntr"]
                if batch_data:
                    all_data.extend(batch_data)
            elif isinstance(response_data, list):
                all_data.extend(response_data)
            elif isinstance(response_data, dict) and response_data:
                all_data.append(response_data)
            
            # Check if there's more data to fetch
            response_cont_yn = response.headers.get("cont-yn", "N")
            response_next_key = response.headers.get("next-key")
            
            if response_cont_yn == "Y" and response_next_key:
                cont_yn = "Y"
                next_key = response_next_key
            else:
                # No more data to fetch
                break
        
        # Prepare final result
        result = {
            "status_code": 200,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "qry_tp": qry_tp,
            "sell_tp": sell_tp,
            "stex_tp": stex_tp,
            "stk_cd": stk_cd,
            "ord_no": ord_no,
            "total_requests": request_count,
            "total_records": len(all_data),
            "execution_data": all_data,
            "message": f"Successfully retrieved {len(all_data)} records in {request_count} requests"
        }
        
        # Add warning if we hit the max requests limit
        if request_count >= max_requests:
            result["warning"] = f"Reached maximum request limit ({max_requests}). There may be more data available."
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Execution info endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_unexecuted_orders(
    client: KiwoomClient, 
    all_stk_tp: str,
    trde_tp: str,
    stex_tp: str,
    stk_cd: str = "",
    max_requests: int = 10
) -> Dict[str, Any]:
    """
    Get unexecuted orders with automatic pagination.
    Automatically handles continuous inquiry to fetch all available data.
    
    Args:
        client: KiwoomClient instance
        all_stk_tp: 전체종목구분 (All Stock Type: "0"=전체, "1"=종목)
        trde_tp: 매매구분 (Trade Type: "0"=전체, "1"=매도, "2"=매수)
        stex_tp: 거래소구분 (Exchange Type: "0"=통합, "1"=KRX, "2"=NXT)
        stk_cd: 종목코드 (Stock Code, optional, e.g., "005930")
        max_requests: Maximum number of API requests to prevent infinite loops (default: 10)
        
    Returns:
        Complete unexecuted orders information with all paginated data including:
        - 계좌번호, 주문번호, 관리사번
        - 종목코드, 업무구분, 주문상태, 종목명
        - 주문수량, 주문가격, 미체결수량
        - 체결누계금액, 원주문번호, 주문구분
        - 매매구분, 시간, 체결번호
        - 체결가, 체결량, 현재가
        - 매도호가, 매수호가, 단위체결가/량
        - 당일매매수수료, 당일매매세금
        - 개인투자자, 거래소구분, SOR 여부값, 스톱가
    """
    try:
        # Use the actual Kiwoom API for unexecuted orders
        api_info = ACCOUNT_APIS["UNEXECUTED_ORDERS"]
        
        all_data = []
        cont_yn = "N"
        next_key = None
        request_count = 0
        
        while request_count < max_requests:
            # Prepare request data according to API spec
            request_data = {
                "all_stk_tp": all_stk_tp,
                "trde_tp": trde_tp,
                "stex_tp": stex_tp
            }
            
            # Add optional parameters if provided
            if stk_cd:
                request_data["stk_cd"] = stk_cd
            
            # Prepare headers
            headers = {
                "api-id": api_info.api_id,
                "cont-yn": cont_yn
            }
            
            if next_key:
                headers["next-key"] = next_key
            
            # Make API request
            response = await client.post(api_info.url, json=request_data, headers=headers)
            request_count += 1
            
            if response.status_code != 200:
                return {
                    "status_code": response.status_code,
                    "api_id": api_info.api_id,
                    "api_name": api_info.name,
                    "all_stk_tp": all_stk_tp,
                    "trde_tp": trde_tp,
                    "stex_tp": stex_tp,
                    "stk_cd": stk_cd,
                    "error": f"API request failed with status {response.status_code}",
                    "message": "Failed to retrieve unexecuted orders"
                }
            
            # Parse response
            response_data = response.json()
            
            # Extract data from response - unexecuted orders returns order data
            if "oso" in response_data:
                batch_data = response_data["oso"]
                if batch_data:
                    all_data.extend(batch_data)
            elif isinstance(response_data, list):
                all_data.extend(response_data)
            elif isinstance(response_data, dict) and response_data:
                all_data.append(response_data)
            
            # Check if there's more data to fetch
            response_cont_yn = response.headers.get("cont-yn", "N")
            response_next_key = response.headers.get("next-key")
            
            if response_cont_yn == "Y" and response_next_key:
                cont_yn = "Y"
                next_key = response_next_key
            else:
                # No more data to fetch
                break
        
        # Prepare final result
        result = {
            "status_code": 200,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "all_stk_tp": all_stk_tp,
            "trde_tp": trde_tp,
            "stex_tp": stex_tp,
            "stk_cd": stk_cd,
            "total_requests": request_count,
            "total_records": len(all_data),
            "unexecuted_orders_data": all_data,
            "message": f"Successfully retrieved {len(all_data)} records in {request_count} requests"
        }
        
        # Add warning if we hit the max requests limit
        if request_count >= max_requests:
            result["warning"] = f"Reached maximum request limit ({max_requests}). There may be more data available."
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Unexecuted orders endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


__all__ = ["get_accounts", "get_account_balance", "get_account_positions", "get_daily_realized_profit_by_stock", "get_account_evaluation", "get_account_current_status", "get_daily_account_profit_detail", "get_orderable_amount", "get_execution_info", "get_unexecuted_orders"]