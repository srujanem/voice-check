const fs = require('fs');
let code = fs.readFileSync('server-config.js', 'utf8');

// Replace the entire block
code = code.replace(/@media \(max-width: 768px\) \{[\s\S]*?\/g, @media (max-width: 768px) {
            #ag-status-badge { 
                bottom: 25px; 
                top: auto; 
                left: 20px; 
                transform: none; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            }
        }
    \`);

fs.writeFileSync('server-config.js', code);
