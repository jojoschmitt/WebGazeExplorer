from experiment import values


class Task:
    def __init__(self, id, experiment_id):
        assert id in [0, 1, 2, 3]
        self.id: int = id
        self.experiment_id: int = experiment_id
        self.randomized_img_order = self._get_img_order()
        self.introduction = self.__get_introduction()

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return str(self.id)

    def _get_img_order(self):
        # random.sample(list(range(32)), 32)
        match self.id:
            case 0:
                return []
            case 1:
                if self.experiment_id <= 8:
                    return [7, 22, 26, 23, 18, 3, 8, 4, 29, 21, 24, 11, 17, 28, 2, 14, 13, 16, 30, 10, 9, 31, 20, 15, 1, 25, 6, 12, 5, 27, 0, 19]
                else:
                    return [16, 14, 26, 8, 15, 23, 20, 18, 27, 30, 29, 6, 2, 0, 4, 11, 7, 31, 17, 21, 24, 5, 13, 28, 19, 12, 3, 22, 9, 25, 1, 10]
            case 2:
                if self.experiment_id <= 8:
                    return [8, 24, 28, 3, 16, 30, 22, 20, 23, 10, 13, 5, 4, 25, 6, 18, 0, 9, 26, 12, 11, 14, 31, 2, 19, 27, 15, 17, 7, 21, 1, 29]
                else:
                    return [28, 16, 13, 3, 27, 14, 20, 30, 9, 22, 17, 5, 8, 18, 26, 15, 10, 12, 21, 1, 25, 0, 24, 19, 4, 6, 7, 2, 23, 29, 31, 11]
            case 3:
                if self.experiment_id <= 8:
                    return [22, 26, 9, 21, 3, 14, 20, 8, 16, 27, 18, 2, 19, 7, 31, 24, 23, 1, 17, 30, 4, 25, 15, 6, 12, 13, 28, 11, 10, 5, 29, 0]
                else:
                    return [24, 16, 4, 1, 20, 2, 21, 17, 18, 8, 11, 3, 19, 10, 0, 27, 22, 12, 28, 5, 30, 23, 31, 7, 29, 6, 14, 15, 13, 26, 25, 9]
            case _:
                raise ValueError(f"No randomized image order found for task id {self.id}")

    def __get_introduction(self):
        match self.id:
            case 0:
                return ""
            case 1:
                return values.introduction_1
            case 2:
                return values.introduction_2
            case 3:
                return values.introduction_3
            case _:
                raise ValueError(f"No introduction found for task id {self.id}")