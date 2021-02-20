class Reaction:
    """
    :param str name:
    :param List[str] left:
    :param List[str] right:
    :param Formula rate_fn:
    """

    def __init__(self, name, left, right, rate_fn):
        self.name = name
        self.left = left
        self.right = right
        self.rate_function = rate_fn

    """
    Return reaction rate in the given network state
    :param Dict[str, float] n: network state
    :returns float of reaction rate
    """

    def rate(self, n):
        return self.rate_function.compute(n)

    """
    Return change vector of reaction
    :param Dict[str, float] n: Network state
    :returns Dict[str, float] of change vector of reaction
    """

    def change_vector(self, n):
        # How to obtain change vectors:
        # fpm + MmyR -> [k1] fpm:MmyR
        # ---------------------------
        # MmyR -= k1[MmyR][fpm]     | General: if MmyR in left, then MmyR -= (k) * (left1) * (left2)
        # fpm -= k1[MmyR][fpm]
        # fpm:MmyR += k1[MmyR][fpm] | General: if fpm:MmyR in right, then fpm:MmyR += (k_) * (left1) * (left2)

        # fpm:MmyR -> [k_1] fpm + MmyR
        # ---------------------------
        # MmyR += k_1 [fpm:MmyR]
        # fpm += k_1 [fpm:MmyR]
        # fpm:MmyR -= k_1[fpm:MmyR]

        change = dict()

        for x in n:

            if x not in change:
                change[x] = 0

            if x in self.left:
                change[x] -= self.rate(n)

            if x in self.right:
                change[x] += self.rate(n)

        return change

    def __str__(self):
        left = self.left[0] if self.left else "∅"
        right = self.right[0] if self.right else "∅"

        string = "Reaction: " + left + " ⟶ " + right + "\n"
        string += str(self.rate_function)

        return string

    def str_variables(self):
        str_vars = self.rate_function.str_variables()
        string = ""
        if len(str_vars) != 0:
            string = "----- " + self.name + " ----- \n"
            string += str_vars + "\n"

        return string
