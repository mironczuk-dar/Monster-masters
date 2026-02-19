#IMPORTING LIBRARIES
from pygame.math import Vector2 as vector

#CHECKING THE DISTANCE BETWEEN PLAYER CHARACTER AND NPC
def check_connection(radius, entity, target, tolarance = 30):
    relation = vector(target.rect.center) - vector(entity.rect.center)
    if relation.length() > radius:
        return False
    
    if entity.facing_direction == 'left' and relation.x < 0 and abs(relation.y) < tolarance: return True
    if entity.facing_direction == 'right' and relation.x > 0 and abs(relation.y) < tolarance: return True
    if entity.facing_direction == 'up' and relation.y < 0 and abs(relation.x) < tolarance: return True
    if entity.facing_direction == 'down' and relation.y > 0 and abs(relation.x) < tolarance: return True

    return False