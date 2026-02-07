from dataclasses import dataclass

@dataclass(frozen=True)
class TgLinkStatus:
    """Статус привязки Telegram аккаунта"""
    connected: bool
    is_entrepreneur: bool
    
    def is_authentificated_user(self) -> bool:
        return self.connected and not self.is_entrepreneur