document.addEventListener('DOMContentLoaded', function() {

    const class1 = document.getElementById("kc-content-wrapper");
    const class2 = document.getElementById("kc-form");
    const class3 = document.getElementById("kc-social-providers");

    class1.insertBefore(class3, class2);

    // Move specific content from class3 to the beginning of class2
    const hrElement = class3.querySelector('hr');
    const h2Element = class3.querySelector('h2');

    if (h2Element) {
      class2.insertBefore(h2Element, class2.firstChild);
    }
      
    if (hrElement) {
      class2.insertBefore(hrElement, h2Element || class2.firstChild);
    }

});

