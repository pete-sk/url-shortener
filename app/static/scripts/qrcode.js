
// generate QR code
function generateQrCode (link) {
    let value = 'https://' + window.location.hostname + '/' + link;
    let qrCodeImg = new QRious({
        value: value,
        size: 1000,
        padding: 50
    });
    let qrCodeUrl = qrCodeImg.toDataURL("image/jpeg");
    let qrCodeDiv = document.querySelector('#qr-code');
    let qrCodeDownloadButton = document.querySelector('#qr-code-download');
    qrCodeDiv.src = qrCodeUrl;
    qrCodeDownloadButton.href = qrCodeUrl;
}
  
  
// load QR code modal data
function loadQrCodeModal (link) { 
    document.querySelector('#QRcodeModalLabel').innerHTML = '/' + link;
    document.querySelector('#qr-code-download').download = link + '.jpg'
    generateQrCode(link);
}