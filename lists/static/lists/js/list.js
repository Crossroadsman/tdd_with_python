/* create namespace 
   we are explicitly declaring Superlists to be a property of the `window`
   global, giving it a name that no-one else in our project-space is likely
   to use.
   Then we will make `initialize` an attribute of that namespace object
*/
window.Superlists = {};
/* we create the `initialize` function so that we can determine when
   the event listener is created. This is important because the `fixture`
   div in qunit replaces the contents in the page every time a new test
   is run and thus the element to which the listener was attached gets
   removed
*/
window.Superlists.initialize = function () {

    $('input[name="text"]').on('keypress click', function () {
        $('.has-error').hide();
    });
};
