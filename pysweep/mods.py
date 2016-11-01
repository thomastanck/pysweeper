from pysweep.util import own_game_mode

class Mod:
    required_events = []
    game_mode_name = ""

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {}


class GameDisplayMod(Mod):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gamedisplay = self.pysweep.gamedisplay


class Face(GameDisplayMod):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hooks.update({
            ("gamedisplaymanager", "FaceDepress"): [self.on_face_depress],
            ("gamedisplaymanager", "FaceClicked"): [self.on_face_click],
            ("gamedisplaymanager", "FaceUndepress"): [self.on_face_undepress],
        })
        self._old_face_mode = None
        self._is_pressed = False

    @own_game_mode
    def on_face_depress(self, hn, e):
        if not self._is_pressed:
            self._old_face_mode = self.gamedisplay.current_face
            self.gamedisplay.set_face_pressed()
            self._is_pressed = True

    @own_game_mode
    def on_face_click(self, hn, e):
        self.face_button(hn, e)
        self.gamedisplay.set_face_happy()

    @own_game_mode
    def on_face_undepress(self, hn, e):
        self._is_pressed = False
        face_state = self._old_face_mode
        if face_state is None:
            face_state = "happy"
        self.gamedisplay.set_face(face_state)

    def face_button(self, hn, e):
        raise NotImplementedError("face_button must be implemented")
