/* we create the `initialize` function so that we can determine when
   the event listener is created. This is important because the `fixture`
   div in qunit replaces the contents in the page every time a new test
   is run and thus the element to which the listener was attached gets
   removed
*/
const initialize = function () {

    $('input[name="text"]').on('keypress', function () {
        $('.has-error').hide();
    });
};
