// web3.js - Global Web3 Logic using Ethers.js v6

let userAddress = null;

async function connectWallet() {
    if (typeof window.ethereum !== 'undefined') {
        try {
            // Request account access
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            userAddress = accounts[0];
            updateWalletUI();
            return userAddress;
        } catch (error) {
            console.error("User denied account access or error occurred:", error);
            alert("Failed to connect wallet. Please try again.");
        }
    } else {
        alert("MetaMask is not installed. Please install it to use Web3 features.");
    }
}

async function checkWalletConnection() {
    if (typeof window.ethereum !== 'undefined') {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_accounts' });
            if (accounts.length > 0) {
                userAddress = accounts[0];
                updateWalletUI();
            }
        } catch(e) {}
    }
}

function updateWalletUI() {
    const btn = document.getElementById('connectWalletBtn');
    if (btn && userAddress) {
        btn.innerHTML = `<i class="fa-brands fa-ethereum"></i> ${userAddress.substring(0, 6)}...${userAddress.substring(userAddress.length - 4)}`;
        btn.classList.add('connected');
        btn.style.background = 'rgba(139, 92, 246, 0.2)';
        btn.style.color = '#c4b5fd';
        btn.style.borderColor = '#8b5cf6';
    }
    
    // Show mint button if report is available
    const mintBtn = document.getElementById('mint-report-btn');
    if (mintBtn && mintBtn.dataset.ready === "true") {
        mintBtn.style.display = 'flex';
    }
}

async function mintReportToBlockchain(reportDataString) {
    if (!userAddress) {
        alert("Please connect your wallet first!");
        connectWallet();
        return false;
    }

    if (typeof window.ethereum !== 'undefined' && typeof ethers !== 'undefined') {
        try {
            const provider = new ethers.BrowserProvider(window.ethereum);
            const signer = await provider.getSigner();
            
            // Hash the report data to prove authenticity without leaking the whole text on-chain
            const hash = ethers.id(reportDataString); // Keccak256 hash
            
            // Convert hash to hex data payload
            const txData = ethers.hexlify(ethers.toUtf8Bytes(`VoiceCheck_Report:${hash}`));

            // Send a 0-value transaction to self to anchor the data permanently
            const tx = await signer.sendTransaction({
                to: userAddress,
                value: 0,
                data: txData
            });
            
            return tx.hash;
        } catch (error) {
            console.error("Minting failed:", error);
            throw error;
        }
    } else {
        alert("Ethers.js or MetaMask not found.");
        return false;
    }
}

// Auto-check on load
window.addEventListener('DOMContentLoaded', () => {
    checkWalletConnection();
    const btn = document.getElementById('connectWalletBtn');
    if(btn) {
        btn.addEventListener('click', connectWallet);
    }
});
