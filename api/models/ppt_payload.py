from models.document import DocumentContent, DocumentRequest, TextItem

def create_sample_request():
    sample_request = DocumentRequest(
            title="Demo Document",
            pages=[
                DocumentContent(
                    text_items=[
                        TextItem(type="header", content="Welcome"),
                        TextItem(type="paragraph", content="This is a sample slide."),
                    ],
                    images=[
                        #ImageItem(path="sample_image.png")
                    ]
                ),

                DocumentContent(
                    text_items=[
                        TextItem(type="subheader", content="Second Slide"),
                        TextItem(type="paragraph", content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus luctus urna sed urna ultricies ac tempor dui sagittis. In condimentum facilisis porta.\nFusce sed felis eget velit aliquet faucibus. Praesent ac massa at ligula laoreet iaculis."),
                    ],
                    images=[]
                )
            ]
        )
    
    return sample_request