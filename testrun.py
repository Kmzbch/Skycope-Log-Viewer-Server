from testmodels import UserModel, ServiceModel

def test_backref():
    user1 = UserModel(username="user1", role="normal")
    user1.set_password("user1")

    service1 = ServiceModel()
    service1 = ServiceModel(name="Service 1", api_url="abc")

    print(user1.username)
    print(service1.name)
    print(user1.services)
    print(service1.user)

    user1.services = [service1]

    print(user1)
    print(service1)
    print(user1.services)
    print(service1.user)

if __name__ == "__main__":
    test_backref()
