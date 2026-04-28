from .base import Collectible
from .powerups import PowerUp, DamageUp, GetsBigger, BulletTime, ShieldPowerUp, LaserPowerUp
from .trinkets import Trinket, SwiftnessTrinket, OrbitalMiniME

COLLECTIBLE_POOL = [
    # PowerUps
    PowerUp, DamageUp, GetsBigger, BulletTime, ShieldPowerUp, LaserPowerUp, 
    # Trinkets
    SwiftnessTrinket, OrbitalMiniME,
]

