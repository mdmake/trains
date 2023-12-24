class TrainSystem:
    """
    Базовый класс для всех подcистем:
    Каждая подсистема должна:
     - получать информацию о местоположении и ориентации борта (`update_navigation`),
     - получать данные (`receive`),
     - производить обработку данных на текущем такте (`step`),
     - посылать данные (`send`).
    """

    def update_navigation(self, x: float | int, y: float | int, alpha: float | int):
        """
        Получение информации о центре масс поезда

        :param x: координата x поезда
        :param y: координата y поезда
        :param alpha: угол положения поезда относительно оси x против часовой оси
        """
        raise NotImplementedError

    def receive(self, query: dict):
        """
        Получение данные

        :param query: управляющие параметры
        """
        raise NotImplementedError

    def step(self):
        """
        Обработка одного такта состояния системы
        """
        raise NotImplementedError

    def send(self) -> dict:
        """
        Посылка данных
        """
        raise NotImplementedError
