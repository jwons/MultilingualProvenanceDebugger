class DebugRecord:

    def __init__(self, userChoice, programInfo, userAnnotation):
        self._userChoice = userChoice
        self._programInfo = programInfo
        self._userAnnotation = userAnnotation

    def prettyPrint(self):
        print(f"Developer action: {self._userChoice}")
        print("Program info:\n")
        print(self._programInfo)
        if self._userAnnotation is not None:
            print(f"Annotation: {self._userAnnotation}")

    def setAnnotation(self, annotation):
        self._userAnnotation = annotation

    def writeDict(self):
        asDict = {}
        asDict["userAction"] = self._userChoice
        asDict["programInfo"] = self._programInfo
        asDict["userAnnotation"] = self._userAnnotation
        return asDict

    @staticmethod
    def fromDict(contentDict):
        return DebugRecord(contentDict["userAction"], contentDict["programInfo"], contentDict["userAnnotation"])
