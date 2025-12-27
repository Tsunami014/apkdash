if 'main' not in globals():
    from app import MainApp
    from gui.wind import ScrlWind
    main = MainApp()

    class CreateWind(ScrlWind):
        def _init(self):
            self.title = "New window"
            for c, a in main.apps.items():
                print(f"\020b{c}\020R: {a.NAME}")
            return True
        def _upd(self, k=None):
            if k in main.apps.keys():
                main.setWind(main.apps[k])
                return
            super()._upd(k)

    main._initialise(CreateWind)

