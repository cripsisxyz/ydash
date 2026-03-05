"""
Módulo para obtener precios de ETFs y acciones desde múltiples fuentes
con fallback automático para máxima confiabilidad
"""

import requests
import yfinance as yf
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import streamlit as st

# Mapeo de tickers de Yuh a múltiples fuentes
TICKER_MAPPINGS = {
    # ETFs
    'EQQQ': {
        'yahoo': 'EQQQ.L',
        'symbol': 'EQQQ',
        'isin': 'IE0032077012',
        'exchange': 'LSE',
        'asset_type': 'ETF',
        'name': 'Invesco EQQQ Nasdaq 100 UCITS ETF',
        'aliases': ['Nasdaq 100', 'EQQQ', 'Invesco EQQQ', 'Nasdaq-100']
    },
    'CSSMI': {
        'yahoo': 'CSSMI.SW',
        'symbol': 'CSSMI',
        'isin': 'CH0017142719',
        'exchange': 'SIX',
        'asset_type': 'ETF',
        'name': 'iShares SMI ETF (CH)',
        'aliases': ['SMI', 'Switzerland SMI', 'iShares SMI', 'CSSMI', 'Swiss']
    },
    'SWQ': {
        'yahoo': 'SWQ.SW',
        'symbol': 'SWQ',
        'isin': 'CH0019396990',
        'exchange': 'SIX',
        'asset_type': 'ETF',
        'name': 'Swisscanto (CH) Index Fund Equity Switzerland',
        'aliases': ['Swisscanto', 'SWQ', 'Switzerland', 'Swiss Equity']
    },
    'ZSIL': {
        'yahoo': 'ZSIL.SW',
        'symbol': 'ZSIL',
        'isin': 'CH0019549621',
        'exchange': 'SIX',
        'asset_type': 'ETF',
        'name': 'Swisscanto (CH) Index Fund Equity Silver',
        'aliases': ['Silver', 'ZSIL', 'Swisscanto Silver']
    },
    'SWDA': {
        'yahoo': 'SWDA.L',
        'symbol': 'SWDA',
        'isin': 'IE00B4L5Y983',
        'exchange': 'LSE',
        'asset_type': 'ETF',
        'name': 'iShares MSCI World UCITS ETF',
        'aliases': ['MSCI World', 'World', 'SWDA', 'iShares World']
    },
    'SPY': {
        'yahoo': 'SPY',
        'symbol': 'SPY',
        'isin': 'US78462F1030',
        'exchange': 'NYSE',
        'asset_type': 'ETF',
        'name': 'SPDR S&P 500 ETF Trust',
        'aliases': ['S&P 500', 'SPY', 'SPDR', 'S&P']
    },
    'QQQ': {
        'yahoo': 'QQQ',
        'symbol': 'QQQ',
        'isin': 'US46090E1038',
        'exchange': 'NASDAQ',
        'asset_type': 'ETF',
        'name': 'Invesco QQQ Trust',
        'aliases': ['QQQ', 'Nasdaq-100', 'Invesco QQQ']
    },
    # Stocks
    'AAPL': {
        'yahoo': 'AAPL',
        'symbol': 'AAPL',
        'isin': 'US0378331005',
        'exchange': 'NASDAQ',
        'asset_type': 'Stock',
        'name': 'Apple Inc.',
        'aliases': ['Apple', 'AAPL']
    },
    'MSFT': {
        'yahoo': 'MSFT',
        'symbol': 'MSFT',
        'isin': 'US5949181045',
        'exchange': 'NASDAQ',
        'asset_type': 'Stock',
        'name': 'Microsoft Corporation',
        'aliases': ['Microsoft', 'MSFT']
    },
    'GOOGL': {
        'yahoo': 'GOOGL',
        'symbol': 'GOOGL',
        'isin': 'US02079K3059',
        'exchange': 'NASDAQ',
        'asset_type': 'Stock',
        'name': 'Alphabet Inc.',
        'aliases': ['Google', 'Alphabet', 'GOOGL']
    },
    'TSLA': {
        'yahoo': 'TSLA',
        'symbol': 'TSLA',
        'isin': 'US88160R1014',
        'exchange': 'NASDAQ',
        'asset_type': 'Stock',
        'name': 'Tesla Inc.',
        'aliases': ['Tesla', 'TSLA']
    },
    # Cryptomonedas
    'BTC': {
        'yahoo': 'BTC-USD',
        'symbol': 'BTC',
        'isin': 'N/A',
        'exchange': 'Crypto',
        'asset_type': 'Crypto',
        'name': 'Bitcoin',
        'aliases': ['Bitcoin', 'BTC', 'BTC-USD']
    },
    'ETH': {
        'yahoo': 'ETH-USD',
        'symbol': 'ETH',
        'isin': 'N/A',
        'exchange': 'Crypto',
        'asset_type': 'Crypto',
        'name': 'Ethereum',
        'aliases': ['Ethereum', 'ETH', 'ETH-USD']
    },
    'SOL': {
        'yahoo': 'SOL-USD',
        'symbol': 'SOL',
        'isin': 'N/A',
        'exchange': 'Crypto',
        'asset_type': 'Crypto',
        'name': 'Solana',
        'aliases': ['Solana', 'SOL', 'SOL-USD']
    },
    'XLM': {
        'yahoo': 'XLM-USD',
        'symbol': 'XLM',
        'isin': 'N/A',
        'exchange': 'Crypto',
        'asset_type': 'Crypto',
        'name': 'Stellar',
        'aliases': ['Stellar', 'XLM', 'XLM-USD']
    },
    'ADA': {
        'yahoo': 'ADA-USD',
        'symbol': 'ADA',
        'isin': 'N/A',
        'exchange': 'Crypto',
        'asset_type': 'Crypto',
        'name': 'Cardano',
        'aliases': ['Cardano', 'ADA', 'ADA-USD']
    },
    'DOT': {
        'yahoo': 'DOT-USD',
        'symbol': 'DOT',
        'isin': 'N/A',
        'exchange': 'Crypto',
        'asset_type': 'Crypto',
        'name': 'Polkadot',
        'aliases': ['Polkadot', 'DOT', 'DOT-USD']
    },
}

# Mapeo inverso por nombre para búsqueda flexible
def find_ticker_by_name(name: str) -> Optional[str]:
    """Encuentra un ticker basándose en el nombre o alias"""
    name_lower = name.lower().strip()

    # Búsqueda exacta
    for ticker, info in TICKER_MAPPINGS.items():
        if name_lower == ticker.lower():
            return ticker
        if name_lower == info['name'].lower():
            return ticker

    # Búsqueda por alias
    for ticker, info in TICKER_MAPPINGS.items():
        for alias in info.get('aliases', []):
            if name_lower in alias.lower() or alias.lower() in name_lower:
                return ticker

    # Búsqueda parcial en el nombre
    for ticker, info in TICKER_MAPPINGS.items():
        if name_lower in info['name'].lower():
            return ticker

    return None

# Descripciones detalladas de activos
ASSET_DESCRIPTIONS = {
    'EQQQ': {
        'description': 'Invesco EQQQ Nasdaq 100 UCITS ETF - Replica el índice Nasdaq 100, que incluye las 100 mayores empresas no financieras del Nasdaq.',
        'asset_class': 'Renta Variable',
        'asset_type': 'ETF',
        'region': 'Estados Unidos',
        'sector': 'Tecnología (mayormente)',
        'ter': '0.30%'
    },
    'CSSMI': {
        'description': 'iShares SMI ETF - Replica el Swiss Market Index (SMI), que incluye las 20 mayores empresas suizas.',
        'asset_class': 'Renta Variable',
        'asset_type': 'ETF',
        'region': 'Suiza',
        'sector': 'Diversificado',
        'ter': '0.35%'
    },
    'SWQ': {
        'description': 'Swisscanto Index Fund Equity Switzerland - Fondo indexado que invierte en el mercado de valores suizo.',
        'asset_class': 'Renta Variable',
        'asset_type': 'ETF',
        'region': 'Suiza',
        'sector': 'Diversificado',
        'ter': '0.20%'
    },
    'ZSIL': {
        'description': 'Swisscanto Silver Fund - ETF that invests in physical silver and silver-related securities.',
        'asset_class': 'Commodities',
        'asset_type': 'ETF',
        'region': 'Global',
        'sector': 'Precious Metals',
        'ter': '0.75%'
    },
    'SWDA': {
        'description': 'iShares MSCI World - Exposición a empresas de gran y mediana capitalización en mercados desarrollados.',
        'asset_class': 'Renta Variable',
        'asset_type': 'ETF',
        'region': 'Global',
        'sector': 'Diversificado',
        'ter': '0.20%'
    },
    'BTC': {
        'description': 'Bitcoin - La primera y más grande criptomoneda por capitalización de mercado.',
        'asset_class': 'Criptomoneda',
        'asset_type': 'Crypto',
        'region': 'Global',
        'sector': 'Blockchain',
        'ter': 'N/A'
    },
    'ETH': {
        'description': 'Ethereum - Plataforma descentralizada que permite crear contratos inteligentes y aplicaciones descentralizadas.',
        'asset_class': 'Criptomoneda',
        'asset_type': 'Crypto',
        'region': 'Global',
        'sector': 'Blockchain',
        'ter': 'N/A'
    },
    'SOL': {
        'description': 'Solana - Blockchain de alta velocidad diseñada para aplicaciones descentralizadas y criptomonedas.',
        'asset_class': 'Criptomoneda',
        'asset_type': 'Crypto',
        'region': 'Global',
        'sector': 'Blockchain',
        'ter': 'N/A'
    },
}


class PriceAPI:
    """Clase para manejar múltiples fuentes de precios con fallback"""

    def __init__(self, alpha_vantage_key: Optional[str] = None):
        self.alpha_vantage_key = alpha_vantage_key or "demo"  # Demo key para testing
        self.session = requests.Session()

    def get_price_yahoo(self, ticker: str) -> Optional[float]:
        """Obtiene precio desde Yahoo Finance"""
        try:
            # Intenta búsqueda directa
            ticker_info = TICKER_MAPPINGS.get(ticker, {})

            # Si no se encuentra, intenta búsqueda por nombre
            if not ticker_info:
                matched_ticker = find_ticker_by_name(ticker)
                if matched_ticker:
                    ticker_info = TICKER_MAPPINGS.get(matched_ticker, {})
                    st.info(f"Ticker '{ticker}' mapeado a '{matched_ticker}'")

            yahoo_symbol = ticker_info.get('yahoo', ticker)

            stock = yf.Ticker(yahoo_symbol)
            data = stock.history(period='1d')

            if not data.empty:
                price = float(data['Close'].iloc[-1])
                return price if price > 0 else None
        except Exception as e:
            # Solo mostrar warning si no es un error de red común
            if "Connection" not in str(e):
                st.warning(f"Yahoo Finance error for {ticker}: {str(e)}")
            return None

    def get_price_financialmodelingprep(self, ticker: str) -> Optional[float]:
        """Obtiene precio desde Financial Modeling Prep (API gratuita)"""
        try:
            ticker_info = TICKER_MAPPINGS.get(ticker, {})
            symbol = ticker_info.get('yahoo', ticker)

            # FMP API gratuita (sin key para quote endpoint)
            url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}"

            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    price = data[0].get('price')
                    if price and price > 0:
                        return float(price)
        except Exception as e:
            st.warning(f"Financial Modeling Prep error for {ticker}: {str(e)}")
            return None

    def get_price_six_exchange(self, ticker: str) -> Optional[float]:
        """Intenta obtener precio desde SIX Swiss Exchange (para tickers suizos)"""
        try:
            ticker_info = TICKER_MAPPINGS.get(ticker, {})
            if ticker_info.get('exchange') != 'SIX':
                return None

            # Usar API pública de SIX si está disponible
            # Por ahora, esto es un placeholder para futuras implementaciones
            return None
        except Exception:
            return None

    def get_price_twelve_data(self, ticker: str) -> Optional[float]:
        """Obtiene precio desde Twelve Data (requiere API key)"""
        try:
            # Twelve Data ofrece tier gratuito
            # Por ahora, esto es un placeholder
            return None
        except Exception:
            return None

    def get_current_price(self, ticker: str) -> Tuple[Optional[float], str]:
        """
        Obtiene el precio actual con fallback automático entre múltiples fuentes

        Returns:
            Tuple[Optional[float], str]: (precio, fuente)
        """
        # Intenta Yahoo Finance primero (más confiable y rápido)
        price = self.get_price_yahoo(ticker)
        if price:
            return price, "Yahoo Finance"

        # Intenta Financial Modeling Prep
        price = self.get_price_financialmodelingprep(ticker)
        if price:
            return price, "Financial Modeling Prep"

        # Intenta SIX Exchange para tickers suizos
        price = self.get_price_six_exchange(ticker)
        if price:
            return price, "SIX Exchange"

        # Si todo falla, retorna None
        return None, "No disponible"

    def detect_asset_type(self, ticker: str, yahoo_info: Dict = None) -> str:
        """Dynamically detect asset type from Yahoo Finance data or patterns"""

        # First check hardcoded mappings (for known assets)
        ticker_info = TICKER_MAPPINGS.get(ticker, {})
        if ticker_info.get('asset_type'):
            return ticker_info['asset_type']

        # Try to detect from Yahoo Finance quoteType
        if yahoo_info:
            quote_type = yahoo_info.get('quoteType', '').upper()

            # Map Yahoo Finance quoteType to our asset types
            type_mapping = {
                'ETF': 'ETF',
                'EQUITY': 'Stock',
                'CRYPTOCURRENCY': 'Crypto',
                'MUTUALFUND': 'Mutual Fund',
                'INDEX': 'Index',
                'FUTURE': 'Future',
                'OPTION': 'Option',
                'CURRENCY': 'Currency',
            }

            if quote_type in type_mapping:
                return type_mapping[quote_type]

        # Pattern matching for crypto (usually ends with -USD, -EUR, etc.)
        if '-USD' in ticker or '-EUR' in ticker or ticker in ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'XLM']:
            return 'Crypto'

        # Check if it's likely an ETF by name patterns
        ticker_upper = ticker.upper()
        etf_patterns = ['ETF', 'FUND', 'INDEX', 'UCITS']
        if yahoo_info:
            name = yahoo_info.get('longName', '') or yahoo_info.get('shortName', '')
            if any(pattern in name.upper() for pattern in etf_patterns):
                return 'ETF'

        # Default to Stock if unknown
        return 'Stock'

    def get_ticker_info(self, ticker: str) -> Dict:
        """Obtiene información detallada del ticker"""
        try:
            # Primero intenta obtener info de Yahoo
            ticker_info = TICKER_MAPPINGS.get(ticker, {})

            # Si no se encuentra, intenta búsqueda por nombre
            if not ticker_info:
                matched_ticker = find_ticker_by_name(ticker)
                if matched_ticker:
                    ticker_info = TICKER_MAPPINGS.get(matched_ticker, {})

            yahoo_symbol = ticker_info.get('yahoo', ticker)

            stock = yf.Ticker(yahoo_symbol)
            info = stock.info

            # Dynamically detect asset type
            asset_type = self.detect_asset_type(ticker, info)

            # Combina info de Yahoo con info local
            local_info = ASSET_DESCRIPTIONS.get(ticker, {})

            return {
                'name': ticker_info.get('name', info.get('longName', info.get('shortName', ticker))),
                'symbol': ticker,
                'isin': ticker_info.get('isin', 'N/A'),
                'exchange': ticker_info.get('exchange', info.get('exchange', 'N/A')),
                'asset_type': asset_type,
                'currency': info.get('currency', 'CHF'),
                'description': local_info.get('description', info.get('longBusinessSummary', 'N/A')),
                'asset_class': local_info.get('asset_class', 'N/A'),
                'region': local_info.get('region', 'N/A'),
                'sector': local_info.get('sector', info.get('sector', 'N/A')),
                'ter': local_info.get('ter', 'N/A'),
                'website': info.get('website', ''),
                'market_cap': info.get('marketCap', 'N/A'),
            }
        except Exception as e:
            # Fallback a información local
            ticker_info = TICKER_MAPPINGS.get(ticker, {})
            local_info = ASSET_DESCRIPTIONS.get(ticker, {})

            # Try to detect asset type even without Yahoo data
            asset_type = self.detect_asset_type(ticker, None)

            return {
                'name': ticker_info.get('name', ticker),
                'symbol': ticker,
                'isin': ticker_info.get('isin', 'N/A'),
                'exchange': ticker_info.get('exchange', 'N/A'),
                'asset_type': asset_type,
                'currency': 'CHF',
                'description': local_info.get('description', 'N/A'),
                'asset_class': local_info.get('asset_class', 'N/A'),
                'region': local_info.get('region', 'N/A'),
                'sector': local_info.get('sector', 'N/A'),
                'ter': local_info.get('ter', 'N/A'),
                'website': '',
                'market_cap': 'N/A',
            }

    def get_historical_data(self, ticker: str, start_date: datetime, end_date: datetime):
        """Obtiene datos históricos"""
        try:
            ticker_info = TICKER_MAPPINGS.get(ticker, {})
            yahoo_symbol = ticker_info.get('yahoo', ticker)

            stock = yf.Ticker(yahoo_symbol)
            data = stock.history(start=start_date, end=end_date)
            return data
        except Exception:
            return None


# Instancia global
price_api = PriceAPI()


def get_current_price(ticker: str) -> Tuple[Optional[float], str]:
    """Función helper para obtener precio actual"""
    return price_api.get_current_price(ticker)


def get_ticker_info(ticker: str) -> Dict:
    """Función helper para obtener info del ticker"""
    return price_api.get_ticker_info(ticker)


def get_historical_data(ticker: str, start_date: datetime, end_date: datetime):
    """Función helper para obtener datos históricos"""
    return price_api.get_historical_data(ticker, start_date, end_date)
