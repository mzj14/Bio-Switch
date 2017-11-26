from urllib.request import Request, urlopen
from time import sleep
import xml.sax


class MovieHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurNum = 0
        self.CurrentData = ""
        self.Key = ""
        self.VersionId = ""
        self.IsLatest = ""
        self.LastModified = ""
        self.ETag = ""
        self.Size = ""
        self.StorageClass = ""

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "Version":
            print("*****Version*****")

    def endElement(self, tag):
        if self.CurrentData == "Key":
            print("Key:", self.Key)
        elif self.CurrentData == "VersionId":
            print("VersionId:", self.VersionId)
            req = Request("https://s3-eu-west-1.amazonaws.com/helvar-stream/thermaldata.png?versionId="+self.VersionId)
            response = urlopen(req)
            cur = response.read()
            with open("img\\"+str(self.CurNum)+".png", "wb") as fp:
                fp.write(cur)
                print("Downloading Picture No."+str(self.CurNum)+" Done!")
            self.CurNum += 1
        elif self.CurrentData == "IsLatest":
            print("IsLatest:", self.IsLatest)
        elif self.CurrentData == "LastModified":
            print("LastModified:", self.LastModified)
        elif self.CurrentData == "ETag":
            print("ETag:", self.ETag)
        elif self.CurrentData == "Size":
            print("Size:", self.Size)
        elif self.CurrentData == "StorageClass":
            print("StorageClass:", self.StorageClass)

        self.CurrentData = ""

    def characters(self, content):
        if self.CurrentData == "Key":
            self.Key = content
        elif self.CurrentData == "VersionId":
            self.VersionId = content
        elif self.CurrentData == "IsLatest":
            self.IsLatest = content
        elif self.CurrentData == "LastModified":
            self.LastModified = content
        elif self.CurrentData == "ETag":
            self.ETag = content
        elif self.CurrentData == "Size":
            self.Size = content
        elif self.CurrentData == "StorageClass":
            self.StorageClass = content


if __name__ == "__main__":
    headers = {
        'Accept': 'application/xml'
    }

    request = Request('https://s3-eu-west-1.amazonaws.com/helvar-stream/?versions&prefix=thermaldata.png',
                      headers=headers)

    xml_response = urlopen(request).read()

    xml_str = xml_response.decode('utf-8')

    with open('thermaldatalist.xml', 'w') as f:
        f.write(xml_str)

    # print(xml_response)
    # 创建一个 XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # 重写 ContextHandler
    Handler = MovieHandler()
    parser.setContentHandler(Handler)

    parser.parse("thermaldatalist.xml")


