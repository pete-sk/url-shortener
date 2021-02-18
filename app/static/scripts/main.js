
// popover
$(function () {
  $('[data-toggle="popover"]').popover({
    delay: {
    "hide": 2000
    }
  })
})


// copy link to clipboard
function copyToClipboard (link) {
  let copyText = document.querySelector(`#link-${link}`).innerHTML;
  document.querySelector('#tmp-input').innerHTML = `<input type="text" value="${copyText}">`;
  copyInput = document.querySelector('#tmp-input input');
  copyInput.select();
  copyInput.setSelectionRange(0, 999); /*For mobile devices*/
  document.execCommand('copy');
  document.querySelector('#tmp-input').innerHTML = '';
}