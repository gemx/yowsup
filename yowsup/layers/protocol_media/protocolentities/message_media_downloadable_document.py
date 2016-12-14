from yowsup.structs import ProtocolEntity, ProtocolTreeNode
from .message_media_downloadable import DownloadableMediaMessageProtocolEntity
from .builder_message_media_downloadable import DownloadableMediaMessageBuilder
from yowsup.layers.protocol_messages.proto.wa_pb2 import ImageMessage
from yowsup.common.tools import ImageTools

class DocumentDownloadableMediaMessageProtocolEntity(DownloadableMediaMessageProtocolEntity):
    '''
    <message t="{{TIME_STAMP}}" from="{{CONTACT_JID}}"
        offline="{{OFFLINE}}" type="text" id="{{MESSAGE_ID}}" notify="{{NOTIFY_NAME}}">
        <media type="{{DOWNLOADABLE_MEDIA_TYPE: (image | audio | video | document)}}"
            mimetype="{{MIME_TYPE}}"
            filehash="{{FILE_HASH}}"
            url="{{DOWNLOAD_URL}}"
            ip="{{IP}}"
            size="{{MEDIA SIZE}}"
            file="{{FILENAME}}"


            encoding="{{ENCODING}}"
            pages="{{page count}}"

            > {{THUMBNAIL_RAWDATA (JPEG?)}}
        </media>
    </message>
    '''
    def __init__(self,
            mimeType, fileHash, url, ip, size, fileName,
            encoding, pages, caption = None, mediaKey = None,
            _id = None, _from = None, to = None, notify = None, timestamp = None,
            participant = None, preview = None, offline = None, retry = None):

        super(ImageDownloadableMediaMessageProtocolEntity, self).__init__("image",
            mimeType, fileHash, url, ip, size, fileName, mediaKey,
            _id, _from, to, notify, timestamp, participant, preview, offline, retry)
        self.setImageProps(encoding, pages, caption)

    def __str__(self):
        out  = super(DocumentDownloadableMediaMessageProtocolEntity, self).__str__()
        out += "Encoding: %s\n" % self.encoding
        out += "Pages: %s\n" % self.pages
        if self.caption:
            out += "Caption: %s\n" % self.caption
        return out

    def setDocumentProps(self, encoding, pages, caption):
        self.encoding   = encoding
        self.pages      = int(pages)
        self.caption    = caption

    def getCaption(self):
        return self.caption

    def toProtocolTreeNode(self):
        node = super(ImageDownloadableMediaMessageProtocolEntity, self).toProtocolTreeNode()
        mediaNode = node.getChild("media")

        mediaNode.setAttribute("encoding",  self.encoding)
        mediaNode.setAttribute("pages",     str(self.pages))
        if self.caption:
            mediaNode.setAttribute("caption", self.caption)

        return node

    def toProtobufMessage(self):
        document_message = DocumentMessage()
        document_message.url = self.url
        document_message.page_coubt = self.pages
        document_message.mime_type = self.mimeType
        document_message.file_sha256 = self.fileHash
        document_message.file_length = self.size
        document_message.caption = self.caption
        document_message.jpeg_thumbnail = self.preview
        document_message.media_key = self.mediaKey

        return document_message

    @staticmethod
    def fromProtocolTreeNode(node):
        entity = DownloadableMediaMessageProtocolEntity.fromProtocolTreeNode(node)
        entity.__class__ = DocumentDownloadableMediaMessageProtocolEntity
        mediaNode = node.getChild("media")
        entity.setDocumentProps(
            mediaNode.getAttributeValue("encoding"),
            mediaNode.getAttributeValue("pages"),
            mediaNode.getAttributeValue("caption"),
        )
        return entity


    @staticmethod
    def getBuilder(jid, filepath):
        return DownloadableMediaMessageBuilder(DocumentDownloadableMediaMessageProtocolEntity, jid, filepath)

    @staticmethod
    def fromBuilder(builder):
        builder.getOrSet("preview", lambda: ImageTools.generatePreviewFromImage(builder.getOriginalFilepath()))
        filepath = builder.getFilepath()
        caption = builder.get("caption")
        dimensions = builder.get("dimensions",  ImageTools.getImageDimensions(builder.getOriginalFilepath()))
        assert dimensions, "Could not determine image dimensions"
        width, height = dimensions

        entity = DownloadableMediaMessageProtocolEntity.fromBuilder(builder)
        entity.__class__ = builder.cls
        entity.setImageProps("raw", width, height, caption)
        return entity

    @staticmethod
    def fromFilePath(path, url, ip, to, mimeType = None, caption = None, dimensions = None):
        builder = ImageDownloadableMediaMessageProtocolEntity.getBuilder(to, path)
        builder.set("url", url)
        builder.set("ip", ip)
        builder.set("caption", caption)
        builder.set("mimetype", mimeType)
        builder.set("dimensions", dimensions)
        return DocumentDownloadableMediaMessageProtocolEntity.fromBuilder(builder)
