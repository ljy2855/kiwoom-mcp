"""Kiwoom OpenAPI constants including API IDs, names, and URLs."""

from typing import Dict, NamedTuple
from enum import Enum


class APICategory(Enum):
    """API category enumeration."""
    OAUTH = "OAuth 인증"
    STOCK_INFO = "종목정보"
    MARKET_DATA = "시세"
    ACCOUNT = "계좌"
    ORDER = "주문"
    CREDIT_ORDER = "신용주문"
    RANKING = "순위정보"
    INSTITUTION_FOREIGN = "기관/외국인"
    SECTOR = "업종"
    CHART = "차트"
    ELW = "ELW"
    ETF = "ETF"
    SHORT_SELLING = "공매도"
    LENDING = "대차거래"
    THEME = "테마"
    CONDITION_SEARCH = "조건검색"
    GOLD = "금현물"


class APIInfo(NamedTuple):
    """API information structure."""
    api_id: str
    name: str
    category: APICategory
    subcategory: str
    url: str


# OAuth Authentication APIs
OAUTH_APIS = {
    "TOKEN_ISSUE": APIInfo("au10001", "접근토큰 발급", APICategory.OAUTH, "접근토큰발급", "/oauth2/token"),
    "TOKEN_REVOKE": APIInfo("au10002", "접근토큰폐기", APICategory.OAUTH, "접근토큰폐기", "/oauth2/revoke"),
}

# Stock Information APIs
STOCK_INFO_APIS = {
    "REAL_TIME_RANKING": APIInfo("ka00198", "실시간종목조회순위", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "BASIC_INFO": APIInfo("ka10001", "주식기본정보요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "TRADER_INFO": APIInfo("ka10002", "주식거래원요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "EXECUTION_INFO": APIInfo("ka10003", "체결정보요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "CREDIT_TRADING_TREND": APIInfo("ka10013", "신용매매동향요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "DAILY_TRADING_DETAIL": APIInfo("ka10015", "일별거래상세요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "NEW_HIGH_LOW": APIInfo("ka10016", "신고저가요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "UPPER_LOWER_LIMIT": APIInfo("ka10017", "상하한가요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "HIGH_LOW_PROXIMITY": APIInfo("ka10018", "고저가근접요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "PRICE_SURGE_DROP": APIInfo("ka10019", "가격급등락요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "VOLUME_RENEWAL": APIInfo("ka10024", "거래량갱신요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "SUPPLY_CONCENTRATION": APIInfo("ka10025", "매물대집중요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "HIGH_LOW_PER": APIInfo("ka10026", "고저PER요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "OPEN_PRICE_RATIO": APIInfo("ka10028", "시가대비등락률요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "SAME_DAY_TRADING": APIInfo("ka10055", "당일전일체결량요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "INVESTOR_DAILY_TRADING": APIInfo("ka10058", "투자자별일별매매종목요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "INVESTOR_INSTITUTION_BY_STOCK": APIInfo("ka10059", "종목별투자자기관별요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "INVESTOR_INSTITUTION_TOTAL": APIInfo("ka10061", "종목별투자자기관별합계요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "TRADER_INSTANT_VOLUME": APIInfo("ka10052", "거래원순간거래량요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "VOLATILITY_CIRCUIT_BREAKER": APIInfo("ka10054", "변동성완화장치발동종목요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "WATCHLIST_INFO": APIInfo("ka10095", "관심종목정보요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "STOCK_INFO_LIST": APIInfo("ka10099", "종목정보 리스트", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "STOCK_INFO_DETAIL": APIInfo("ka10100", "종목정보 조회", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "SECTOR_CODE_LIST": APIInfo("ka10101", "업종코드 리스트", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "MEMBER_COMPANY_LIST": APIInfo("ka10102", "회원사 리스트", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "PROGRAM_TRADING_TOP_50": APIInfo("ka90003", "프로그램순매수상위50요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
    "PROGRAM_TRADING_BY_STOCK": APIInfo("ka90004", "종목별프로그램매매현황요청", APICategory.STOCK_INFO, "종목정보", "/api/dostk/stkinfo"),
}

# Market Data APIs
MARKET_DATA_APIS = {
    "QUOTE": APIInfo("ka10004", "주식호가요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "DAILY_WEEKLY_MONTHLY": APIInfo("ka10005", "주식일주월시분요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "TIME_MINUTE": APIInfo("ka10006", "주식시분요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "MARKET_STATUS": APIInfo("ka10007", "시세표성정보요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "WARRANT_ALL_QUOTE": APIInfo("ka10011", "신주인수권전체시세요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "INSTITUTION_DAILY": APIInfo("ka10044", "일별기관매매종목요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "INSTITUTION_TREND_BY_STOCK": APIInfo("ka10045", "종목별기관매매추이요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "EXECUTION_STRENGTH_HOURLY": APIInfo("ka10046", "체결강도추이시간별요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "EXECUTION_STRENGTH_DAILY": APIInfo("ka10047", "체결강도추이일별요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "DAILY_PRICE": APIInfo("ka10086", "일별주가요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "AFTER_HOURS_SINGLE": APIInfo("ka10087", "시간외단일가요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "MEMBER_COMPANY_TREND": APIInfo("ka10078", "증권사별종목매매동향요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "INVESTOR_INTRADAY": APIInfo("ka10062", "장중투자자별매매요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "INVESTOR_AFTER_CLOSE": APIInfo("ka10066", "장마감후투자자별매매요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "PROGRAM_TRADING_HOURLY": APIInfo("ka90005", "프로그램매매추이요청 시간대별", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "PROGRAM_PROFIT_TREND": APIInfo("ka90006", "프로그램매매차익잔고추이요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "PROGRAM_ACCUMULATED_TREND": APIInfo("ka90007", "프로그램매매누적추이요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "PROGRAM_TREND_BY_STOCK_HOURLY": APIInfo("ka90008", "종목시간별프로그램매매추이요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "PROGRAM_TREND_DAILY": APIInfo("ka90010", "프로그램매매추이요청 일자별", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
    "PROGRAM_TREND_BY_STOCK_DAILY": APIInfo("ka90013", "종목일별프로그램매매추이요청", APICategory.MARKET_DATA, "시세", "/api/dostk/mrkcond"),
}

# Account APIs
ACCOUNT_APIS = {
    "DAILY_BALANCE_PROFIT": APIInfo("ka01690", "일별잔고수익률", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "UNEXECUTED": APIInfo("ka10071", "미체결요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "EXECUTED": APIInfo("ka10072", "체결요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "DAILY_REALIZED_PROFIT": APIInfo("ka10073", "당일실현손익상세요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "ACCOUNT_PROFIT": APIInfo("ka10081", "계좌수익률요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "DAILY_TRADING_LOG": APIInfo("ka10169", "당일매매일지요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "DEPOSIT_DETAIL": APIInfo("kt00001", "예수금상세현황요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "DAILY_ESTIMATED_ASSET": APIInfo("kt00002", "일별추정예탁자산현황요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "ESTIMATED_ASSET": APIInfo("kt00003", "추정자산조회요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "ACCOUNT_EVALUATION": APIInfo("kt00004", "계좌평가현황요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "EXECUTED_BALANCE": APIInfo("kt00005", "체결잔고요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "ORDER_EXECUTION_DETAIL": APIInfo("kt00007", "계좌별주문체결내역상세요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "NEXT_DAY_SETTLEMENT": APIInfo("kt00008", "계좌별익일결제예정내역요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "ORDER_EXECUTION_STATUS": APIInfo("kt00009", "계좌별주문체결현황요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "ORDER_WITHDRAWABLE": APIInfo("kt00010", "주문인출가능금액요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "MARGIN_RATE_ORDERABLE": APIInfo("kt00011", "증거금율별주문가능수량조회요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "CREDIT_MARGIN_ORDERABLE": APIInfo("kt00012", "신용보증금율별주문가능수량조회요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "MARGIN_DETAIL": APIInfo("kt00013", "증거금세부내역조회요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "COMMISSION_TRADING_HISTORY": APIInfo("kt00015", "위탁종합거래내역요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "DAILY_ACCOUNT_PROFIT_DETAIL": APIInfo("kt00016", "일별계좌수익률상세현황요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "ACCOUNT_DAILY_STATUS": APIInfo("kt00017", "계좌별당일현황요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
    "ACCOUNT_EVALUATION_BALANCE": APIInfo("kt00018", "계좌평가잔고내역요청", APICategory.ACCOUNT, "계좌", "/api/dostk/acnt"),
}

# Order APIs
ORDER_APIS = {
    "BUY_ORDER": APIInfo("kt10000", "주식 매수주문", APICategory.ORDER, "주문", "/api/dostk/ordr"),
    "SELL_ORDER": APIInfo("kt10001", "주식 매도주문", APICategory.ORDER, "주문", "/api/dostk/ordr"),
    "MODIFY_ORDER": APIInfo("kt10002", "주식 정정주문", APICategory.ORDER, "주문", "/api/dostk/ordr"),
    "CANCEL_ORDER": APIInfo("kt10003", "주식 취소주문", APICategory.ORDER, "주문", "/api/dostk/ordr"),
}

# Credit Order APIs
CREDIT_ORDER_APIS = {
    "CREDIT_BUY_ORDER": APIInfo("kt10006", "신용 매수주문", APICategory.CREDIT_ORDER, "신용주문", "/api/dostk/crdordr"),
    "CREDIT_SELL_ORDER": APIInfo("kt10007", "신용 매도주문", APICategory.CREDIT_ORDER, "신용주문", "/api/dostk/crdordr"),
    "CREDIT_MODIFY_ORDER": APIInfo("kt10008", "신용 정정주문", APICategory.CREDIT_ORDER, "신용주문", "/api/dostk/crdordr"),
    "CREDIT_CANCEL_ORDER": APIInfo("kt10009", "신용 취소주문", APICategory.CREDIT_ORDER, "신용주문", "/api/dostk/crdordr"),
}

# Chart APIs
CHART_APIS = {
    "TICK_CHART": APIInfo("ka10079", "주식틱차트조회요청", APICategory.CHART, "차트", "/api/dostk/chart"),
    "MINUTE_CHART": APIInfo("ka10080", "주식분봉차트조회요청", APICategory.CHART, "차트", "/api/dostk/chart"),
    "DAILY_CHART": APIInfo("ka10081", "주식일봉차트조회요청", APICategory.CHART, "차트", "/api/dostk/chart"),
    "WEEKLY_CHART": APIInfo("ka10082", "주식주봉차트조회요청", APICategory.CHART, "차트", "/api/dostk/chart"),
    "MONTHLY_CHART": APIInfo("ka10083", "주식월봉차트조회요청", APICategory.CHART, "차트", "/api/dostk/chart"),
    "YEARLY_CHART": APIInfo("ka10091", "주식년봉차트조회요청", APICategory.CHART, "차트", "/api/dostk/chart"),
    "INVESTOR_INSTITUTION_CHART": APIInfo("ka10056", "종목별투자자기관별차트요청", APICategory.CHART, "차트", "/api/dostk/chart"),
    "INVESTOR_INTRADAY_CHART": APIInfo("ka10060", "장중투자자별매매차트요청", APICategory.CHART, "차트", "/api/dostk/chart"),
}

# All APIs combined
ALL_APIS = {
    **OAUTH_APIS,
    **STOCK_INFO_APIS,
    **MARKET_DATA_APIS,
    **ACCOUNT_APIS,
    **ORDER_APIS,
    **CREDIT_ORDER_APIS,
    **CHART_APIS,
}

# API lookup by ID
API_BY_ID = {api.api_id: api for api in ALL_APIS.values()}

# API lookup by category
API_BY_CATEGORY: Dict[APICategory, Dict[str, APIInfo]] = {
    APICategory.OAUTH: OAUTH_APIS,
    APICategory.STOCK_INFO: STOCK_INFO_APIS,
    APICategory.MARKET_DATA: MARKET_DATA_APIS,
    APICategory.ACCOUNT: ACCOUNT_APIS,
    APICategory.ORDER: ORDER_APIS,
    APICategory.CREDIT_ORDER: CREDIT_ORDER_APIS,
    APICategory.CHART: CHART_APIS,
}


def get_api_info(api_key: str) -> APIInfo:
    """Get API information by key."""
    return ALL_APIS[api_key]


def get_api_by_id(api_id: str) -> APIInfo:
    """Get API information by API ID."""
    return API_BY_ID[api_id]


def get_apis_by_category(category: APICategory) -> Dict[str, APIInfo]:
    """Get all APIs by category."""
    return API_BY_CATEGORY[category]


__all__ = [
    "APICategory", "APIInfo", "ALL_APIS", "API_BY_ID", "API_BY_CATEGORY",
    "OAUTH_APIS", "STOCK_INFO_APIS", "MARKET_DATA_APIS", "ACCOUNT_APIS", 
    "ORDER_APIS", "CREDIT_ORDER_APIS", "CHART_APIS",
    "get_api_info", "get_api_by_id", "get_apis_by_category"
]
