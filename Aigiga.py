from gigachat import GigaChat
import Tokens

giga = GigaChat(
    credentials = Tokens.GiGiaChat_Token,
    scope = "GIGACHAT_API_PERS",
    model = "GigaChat-2-Pro",
    ca_bundle_file = Tokens.Ca_file,
    verify_ssl_certs = True,
)

if __name__ == "__main__":
    print(giga.chat("Привет").choices[0].message.content)