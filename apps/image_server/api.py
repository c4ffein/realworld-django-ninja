from base64 import b64decode
from typing import Any

from django.http import HttpResponse
from ninja import Router

router = Router()


# This is a public domain file
# https://en.m.wikipedia.org/wiki/File:Example.png
png_file = b64decode(
    b"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"
)


# This is a CC BY-SA 3.0 file - https://creativecommons.org/licenses/by-sa/3.0/deed.en
# Credits to Toytoy - https://en.wikipedia.org/wiki/User:Toytoy
# https://commons.wikimedia.org/wiki/File:JPEG_example_JPG_RIP_001.jpg
jpg_file = b64decode(
    b"/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCADqATkDASIAAhEBAxEB/8QAFwABAQEBAAAAAAAAAAAAAAAAAAECA//EACQQAQEBAAIBBAMBAQEBAAAAAAABESExQQISUXFhgZGxocHw/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAWEQEBAQAAAAAAAAAAAAAAAAAAEQH/2gAMAwEAAhEDEQA/AMriLyCKgg1gQwCgs4FTMOdutepjQak+FzMSVqgxZdRdPPIIvH5WzzGdBriphtTeAXg2ZjKA1pqKDUGZca3foBek8gFv8Ie3fKdA1qb8s7hoL6eLVt51FsAnql3Ut1M7AWbflLMDkEMX/F6/YjK/pADFQAUNA6alYagKk72m/j9p4Bq2fDDSYKLNXPNLoHE/NT6RYC31cJxZ3yWVM+aBYi/S2ZgiAsnYJx5D21vPmqrm3PTfpQQwyAC8JZvSKDni41ZrMuUVVl+Uz9w9v/1QWrZsZ5nFPHYH+JZyureQSF5M+fJ0CAfwRAVRBQA1DAWVUayoJUWoDpsxntPsueBV4+VxhdyAtv8AjOLGpIDMLbeGvbF4iozJfr/WukAVABAXAQXEAAASzVAZdO2WNordm+emFl7XcQSNZiFtv0C9w90nhJf4mA1u+GcJFwIyAqL/AOovwgGNfSRqdIrNa29M0gKCAojU9PAMjWXpckEJFNFEAAXEUBABYz6rZ0ureQc9vyt9XxDF2QAXtABcQAs0AZywkvluJbyipifas52DcyxjlZweAO0xri/hc+wZOEKIu6nSyeToVZyWXwvCg53gW81QQ7aTNAn5dGZJPs1UXURQAUEMCXQLZE93PRZ5hPTgNMrbIzKCm52LZwCs+2M8w2g3sjPuZAXb4IsMAUACzVUGM4/K+md6vEXUUyM5PDR0IxYe6ramih0VNBrS4xoqN8Q1BFQk3yqyAsioioAAKgDSJL4/jQIn5igLrPqtOuf6oOaxbMoAltUAhhIoJiiggrPu+AaOIxtAX3JbaAIaLwi4t9X4T3fg2AFtqcrUUarP20zUDAmqoE0WRBZPNVUVEAAAAVAC8kvih2DSKxOdBqs7Z0l0gI0mKAC4AuHE7ZtBriM+744QAAAAABAFsveIttBICyaikvy1+r/Cen5rWQHIBQa4rIDRqSl5qDWqziqgAAAATA7BpGdqXb2C2+J/UgAtRQBSQtkBWb6vhLbQAAAAAEBRAAAAAUbm+GZNdPxAP+ql2Tjwx7/wIgZ8iKvBk+CJoCXii9gaqZ/qqihAAAEVABGkBFUwBftNkZ3QW34QAAABFAQAVAAAAAARVkl8gs/43sk1jL45LvHArepk+E9XTG35oLqsmIKmLAEygKg0y1AFQBUXwgAAAoBC34S3UAAABAVAAAAAABAUQAVABdRQa1PcYyit2z58M8C4ouM2NXpOEGeWtNZUatiAIoAKIoCoAoG4C9MW6dgIoAIAAAAAAACKWAgL0CAAAALiANCKioNLgM1CrLihmTafkt1EF3SZ5ZVUW4mnIKvAi5fhEURVDWVQBRAAAAAAAAQFRVyAyulgAqCKlF8IqLsEgC9mGoC+IusqCrv5ZEUVOk1RuJfwSLOOkGFi4XPCoYYrNiKauosBGi9ICstM1UAAAAAAFQ0VcTBAXUGgIqGoKhKAzRRUQUAwxoSrGRpkQA/qiosOL9oJptMRRVZa0VUqSiChE6BqMgCwqKqIogAIAqKCKgKoogg0lBFuIKgAAAKNRlf2gqsftsEtZWoAAqAACKoMqAAeSoqp39kL2AqLOlE8rEBFQARYALhigrNC9gGmooLp4TweEQFFBFAECgIoAu0ifIAqAAA//9k="
)


@router.get("/{path}", response={200: Any, 404: Any})
def get_file(request, path: str) -> HttpResponse | tuple[int, None]:
    """
    Not the best way to serve static files obviously, you should store files on another server etc
    Still a good example of how to serve files generated at request time
    """
    if path.endswith(".png"):
        return HttpResponse(png_file, content_type="image/png")
    if path.endswith((".jpg", ".jpeg")):
        return HttpResponse(jpg_file, content_type="image/jpeg")
    return 404, None
