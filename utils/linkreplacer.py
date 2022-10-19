"""
1. removed되는 노드는 신경쓰지 않는다.
2. added 된 노드는 해당 노드의 모든 어트리비우트를 조사해서 replace를 한다.
    text노드의 경우는 어.. 리플레이스를 해야하나... 하면 눈치챌거같긴 한데... 안하면 문제생길수도 있고...
3. attributes 노드는 그냥 target[attributeName]해서 접근하고 replace한다.

다시
1. added 된 노드는 addedNodes[0].attributes를 뒤지면서 replace, innerText도 replace
2. attributes 노드는 target[attributeName] 해서 접근하고 replace
<script>
    const targetNode = document.querySelector('html');
    const config = { attributes: true, childList: true, subtree: true };
    var isFollowing = true;

    const htmlAttrs2ArrayAttrs = (htmlAttrs) => Array.from(htmlAttrs);
    const replace2HTTP = (str) => str.replace("https://", "http://");
    const hasHTTPs = (str) => str.indexOf("https://") != -1;
    
    const callback = (mutationList, observer) => {
        if (isFollowing) {
            isFollowing = false;
            console.log("cancel following edit");
            return;
        }

        console.log(mutationList);
        for (const mutation of mutationList) {
            if (mutation.type === "childList") {
                const node = mutation.addedNodes[0];
                if (node.nodeName === "#text") {
                    continue;
                }
                console.log("childList edit");
                if (hasHTTPs(node.innerHTML)) {
                    node.innerHTML = replace2HTTP(node.innerHTML);
                }
                const htmlAttrs = node.attributes;
                for (const attr of htmlAttrs2ArrayAttrs(htmlAttrs)) {
                    if (hasHTTPs(attr.value)) {
                        attr.value = replace2HTTP(attr.value);
                    }
                }
            } else if (mutation.type === "attributes") {
                console.log("attributes edit");
                const node = mutation.target;
                const attrName = mutation.attributeName;
                const attr = node.attributes[attrName];
                if (hasHTTPs(attr.value)) {
                    attr.value = replace2HTTP(attr.value);
                }
            }
        }
    };
    const observer = new MutationObserver(callback);
    observer.observe(targetNode, config);
</script>
"""

linkreplacer: bytes = \
b"""<script>
    const _0x111 = document.querySelector('html');
    const _0x222 = { attributes: true, childList: true, subtree: true };
    var _0x333 = true;

    const _0x444 = (htmlAttrs) => Array.from(htmlAttrs);
    const _0x555 = (str) => str.replace("https://", "http://");
    const _0x666 = (str) => str.indexOf("https://") != -1;
    
    const _0x777 = (mutationList, observer) => {
        if (_0x333) {
            _0x333 = false;
            console.log("cancel following edit");
            return;
        }

        console.log(mutationList);
        for (const mutation of mutationList) {
            if (mutation.type === "childList") {
                console.log("childList edit");
                const node = mutation.addedNodes[0];
                if (node.innerHTML === undefined) {
                    continue;
                }
                if (_0x666(node.innerHTML)) {
                    node.innerHTML = _0x555(node.innerHTML);
                }
                const htmlAttrs = node.attributes;
                for (const attr of _0x444(htmlAttrs)) {
                    if (_0x666(attr.value)) {
                        attr.value = _0x555(attr.value);
                    }
                }
            } else if (mutation.type === "attributes") {
                console.log("attributes edit");
                const node = mutation.target;
                const attrName = mutation.attributeName;
                const attr = node.attributes[attrName];
                if (_0x666(attr.value)) {
                    attr.value = _0x555(attr.value);
                }
            }
        }
    };
    const _0x888 = new MutationObserver(_0x777);
    _0x888.observe(_0x111, _0x222);
</script>
"""