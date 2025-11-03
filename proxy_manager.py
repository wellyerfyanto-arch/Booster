import requests
import random
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_webshare_proxies(self) -> List[Dict]:
        """Get proxies from WebShare"""
        try:
            # You need to add your WebShare API key in environment variables
            api_key = "YOUR_WEBSHARE_API_KEY"  # Change this or use env var
            response = self.session.get(
                f"https://proxy.webshare.io/api/proxy/list/",
                headers={"Authorization": f"Token {api_key}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                proxies = []
                for proxy in data.get('results', []):
                    proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['proxy_address']}:{proxy['port']}"
                    proxies.append({
                        'http': proxy_url,
                        'https': proxy_url,
                        'source': 'webshare'
                    })
                return proxies
        except Exception as e:
            logger.error(f"WebShare proxy error: {e}")
        return []
    
    def get_proxyscrape_proxies(self) -> List[Dict]:
        """Get proxies from ProxyScrape"""
        try:
            response = self.session.get(
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
                timeout=10
            )
            if response.status_code == 200:
                proxies = []
                for line in response.text.strip().split('\r\n'):
                    if ':' in line:
                        ip, port = line.split(':')
                        proxy_url = f"http://{ip}:{port}"
                        proxies.append({
                            'http': proxy_url,
                            'https': proxy_url,
                            'source': 'proxyscrape'
                        })
                return random.sample(proxies, min(10, len(proxies)))  # Return 10 random proxies
        except Exception as e:
            logger.error(f"ProxyScrape error: {e}")
        return []
    
    def get_iproyal_proxies(self) -> List[Dict]:
        """Get proxies from IPRoyal"""
        try:
            # IPRoyal provides static residential proxies
            # You need to add your IPRoyal credentials
            username = "YOUR_IPROYAL_USERNAME"
            password = "YOUR_IPROYAL_PASSWORD"
            gateway = "gateway.iproyal.com"
            
            ports = ["12323", "12324", "12325"]  # Example ports
            proxies = []
            
            for port in ports:
                proxy_url = f"http://{username}:{password}@{gateway}:{port}"
                proxies.append({
                    'http': proxy_url,
                    'https': proxy_url,
                    'source': 'iproyal'
                })
            
            return proxies
        except Exception as e:
            logger.error(f"IPRoyal proxy error: {e}")
        return []
    
    def get_scrapingant_proxies(self) -> List[Dict]:
        """Get proxies from ScrapingAnt"""
        try:
            # ScrapingAnt rotating proxy service
            api_key = "YOUR_SCRAPINGANT_API_KEY"
            proxy_url = f"http://proxy.scrapingant.com:8080?api_key={api_key}"
            
            return [{
                'http': proxy_url,
                'https': proxy_url,
                'source': 'scrapingant'
            }]
        except Exception as e:
            logger.error(f"ScrapingAnt proxy error: {e}")
        return []
    
    def get_free_proxies(self) -> List[Dict]:
        """Get free proxies from various sources"""
        sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all"
        ]
        
        all_proxies = []
        for source in sources:
            try:
                response = self.session.get(source, timeout=10)
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if ':' in line and not line.startswith('#'):
                            ip, port = line.split(':', 1)
                            proxy_url = f"http://{ip}:{port}"
                            all_proxies.append({
                                'http': proxy_url,
                                'https': proxy_url,
                                'source': 'free'
                            })
            except Exception as e:
                logger.warning(f"Failed to get proxies from {source}: {e}")
                continue
        
        return random.sample(all_proxies, min(20, len(all_proxies)))
    
    def get_all_proxies(self) -> List[Dict]:
        """Get proxies from all available sources"""
        all_proxies = []
        
        # Add free proxies first (most available)
        all_proxies.extend(self.get_free_proxies())
        
        # Add paid proxies (comment out if you don't have credentials)
        # all_proxies.extend(self.get_webshare_proxies())
        # all_proxies.extend(self.get_proxyscrape_proxies())
        # all_proxies.extend(self.get_iproyal_proxies())
        # all_proxies.extend(self.get_scrapingant_proxies())
        
        # Remove duplicates
        unique_proxies = []
        seen = set()
        for proxy in all_proxies:
            proxy_key = proxy['http']
            if proxy_key not in seen:
                seen.add(proxy_key)
                unique_proxies.append(proxy)
        
        logger.info(f"Retrieved {len(unique_proxies)} proxies from {len(set(p['source'] for p in unique_proxies))} sources")
        return unique_proxies
    
    def test_proxy(self, proxy_config: Dict, timeout: int = 5) -> bool:
        """Test if a proxy is working"""
        try:
            response = self.session.get(
                "https://httpbin.org/ip",
                proxies=proxy_config,
                timeout=timeout
            )
            return response.status_code == 200
        except:
            return False
    
    def get_working_proxy(self) -> Optional[Dict]:
        """Get a random working proxy"""
        proxies = self.get_all_proxies()
        
        # Test up to 10 random proxies
        tested_proxies = random.sample(proxies, min(10, len(proxies)))
        
        for proxy in tested_proxies:
            if self.test_proxy(proxy):
                logger.info(f"Using working proxy from {proxy['source']}")
                return proxy
        
        logger.warning("No working proxies found, using direct connection")
        return None
