class A:
    name = 'wanli'

    @property
    def age(self, set_age):
        age = set_age
        return age

    def age1(self, set_age):
        age = set_age
        return age


test = A()
print(test.name)
print(test.age(18))
