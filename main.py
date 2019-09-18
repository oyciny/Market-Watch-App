from Session import Session
import getpass


def main(sess):
    print(sess.buildPreSaleCard("F"))

def initializeSession():
    username = input("username (email): ")
    password = getpass.getpass()
    x = Session(username, password)
    x.login()
    return x


if __name__ == "__main__":
    session = initializeSession()
    main(session)
