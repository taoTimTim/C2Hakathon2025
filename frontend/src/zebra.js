// create the button in the canvas menu on the left that "opens" Zebra
function addZebraButtonToMenu() {
    // <li> contains a <a> that contains 2 <div>
    // the first <div> is the icon for the item in the menu
    // the second <div> is for the name.

    // code for the list item and text:
    let zebraMenuLi = document.createElement('li');
    zebraMenuLi.classList = "menu-item ic-app-header__menu-list-item";

    let zebraMenuLiA = document.createElement('a');
    zebraMenuLiA.onclick = loadZebra;

    zebraMenuLi.appendChild(zebraMenuLiA);

    // code for adding the icon:

    let ZebraMenuDiv_icon = document.createElement('div');
    ZebraMenuDiv_icon.className = "menu-item-icon-container";
    ZebraMenuDiv_icon.ariaHidden = 'true';


    // svg icon currently doesn't work not sure why

    const obj = document.createElement('object');
        
    obj.setAttribute('data', 'src/icons/newsmode.svg');
    obj.setAttribute('type', 'image/svg+xml');

    ZebraMenuDiv_icon.appendChild(obj);

    zebraMenuLiA.appendChild(ZebraMenuDiv_icon);

    let ZebraMenuDiv_text = document.createElement('div');
    ZebraMenuDiv_text.className = "menu-item__text";
    ZebraMenuDiv_text.innerHTML = ('Zebra');

    zebraMenuLiA.appendChild(ZebraMenuDiv_text);

    // add the list item to the menu

    let a = document.getElementById('menu');
    a.appendChild(zebraMenuLi);
}

addZebraButtonToMenu();






function loadZebra() {
    removeNodesFromContent();
    addZebraContent();
}


// removes all the nodes from content
function removeNodesFromContent() {
    content = document.getElementById('content');
  while (content.firstChild) {
    content.removeChild(content.firstChild);
  }
}

function h1(text) {
    
    let titleContainer = document.createElement('div');
    titleContainer.classLIst="";
    title.id = 'dashboard_header_container';
    title.class = 'ic-Dashboard-header';

    let t = document.createElement('div');
    t.classList="large ic-Dashboard-header__layout";

    let h = document.createElement('h1');
    h.class='large';
    h.innerHTML=(text);

    t.appendChild(h);
    titleContainer.appendChild(t);

    return titleContainer;
}

function addZebraContent() {
    content = document.getElementById('content');
    // content.appendChild(h1('Zebra'));

    // pageUrl = browser.runtime.getURL("pages/zebra.html");
    // content.innerHTML = pageUrl;


    // url = browser.runtime.getURL('pages/zebra.html');
    // console.log(url);
    // fetch(url)
    //     .then(response => response.text()) // Get the response as text
    //     .then(html => {
    //         content.innerHTML = html; // Insert the HTML into the div
    //     })
    //     .catch(error => {
    //         console.error('Error fetching content:', error);
    //         content.innerHTML = '<p>Failed to load content.</p>';
    //     });






            // content-script.js
    async function loadAndInjectHTML() {
        try {
            const response = await fetch(browser.runtime.getURL('pages/index.html'));
            const htmlContent = await response.text();

            // Sanitize the HTML content for security
            const sanitizedHTML = DOMPurify.sanitize(htmlContent);

            // Create a temporary element to parse the HTML string into DOM nodes
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = sanitizedHTML;

            // Append the parsed nodes to the desired location in the page's DOM
            document.body.appendChild(content); // Or a more specific target element
        } catch (error) {
            console.error("Error loading or injecting HTML:", error);
        }
    }

    loadAndInjectHTML();
}