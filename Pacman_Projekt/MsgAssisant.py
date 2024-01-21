from spade.message import Message

class MsgAssistant():

    @staticmethod
    def createMsg(sender, to, body, ontology="none", performative="none"):
        msg = Message(
            sender=sender,
            to=to,
            body=body,
            metadata={
                "ontology": ontology,
                "performative": performative,
            },
        )
        return msg
    
    def onMsgReceive(msg, jid="none",):
        if msg:
            print(jid, ": Received message: ", msg.body)
        else:
            print(jid, "Did not receive any message after 10 seconds")

    def printMinuses():
        print("------------")