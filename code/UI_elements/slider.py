import pygame

# SLIDER CLASS (No longer a Sprite)
class Slider:

    # CONSTRUCTOR
    def __init__(s, game, pos, size, min_val=0.0, max_val=1.0, start_val=0.5, on_change=None):
        # PASSING IN GAME AS AN ATTRIBUTE
        s.game = game

        # POSITION AND SIZE
        s.x, s.y = pos
        s.width, s.height = size
        
        # The main track rectangle
        s.track_rect = pygame.Rect(s.x, s.y, s.width, s.height)

        # SLIDER VALUES
        s.min_val = min_val
        s.max_val = max_val
        s.value = start_val
        s.on_change = on_change

        # HANDLING
        s.handle_width = 20
        s.handle_height = s.height + 10
        s.dragging = False
        # The interactive handle rectangle
        s.handle_rect = pygame.Rect(0, 0, s.handle_width, s.handle_height)
        s.update_handle_position()

    # METHOD FOR HANDLING HANDLE POSITION
    def update_handle_position(s):
        # Calculate x based on value
        ratio = (s.value - s.min_val) / (s.max_val - s.min_val)
        handle_x = s.x + int(ratio * (s.width - s.handle_width))
        s.handle_rect.topleft = (handle_x, s.y - (s.handle_height - s.height) // 2)

    # METHOD FOR INPUTS (Renamed from input to handling_events to match OptionsMenu)
    def handling_events(s, events):
        # Get mouse pos relative to the screen (not scaled inside here)
        mouse_pos = s.game.get_scaled_mouse_pos()
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and s.handle_rect.collidepoint(mouse_pos):
                    s.dragging = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    s.dragging = False

        # UPDATING VALUE WHEN DRAGGING
        if s.dragging:
            # Clamping handle within slider range
            new_x = max(s.x, min(mouse_pos[0] - s.handle_width // 2, s.x + s.width - s.handle_width))
            
            # Convert handle position to slider value
            s.value = s.min_val + (new_x - s.x) / (s.width - s.handle_width) * (s.max_val - s.min_val)
            s.update_handle_position() # Keep handle attached to mouse

            if s.on_change:
                s.on_change(s.value)

    # METHOD FOR UPDATING (Now just triggers event handling)
    def update(s, delta_time):
        # The logic is now handled in handling_events for responsiveness
        pass

    # METHOD FOR DRAWING
    def draw(s, surface):
        # DRAWING TRACK
        pygame.draw.rect(surface, (150, 150, 150), s.track_rect)

        # DRAWING FILL
        ratio = (s.value - s.min_val) / (s.max_val - s.min_val)
        fill_width = int(ratio * s.width)
        pygame.draw.rect(surface, (50, 200, 50), (s.x, s.y, fill_width, s.height))

        # DRAWING HANDLE
        pygame.draw.rect(surface, (255, 255, 255), s.handle_rect)