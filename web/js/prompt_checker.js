import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import { $el } from "../../../scripts/ui.js";

const DISABLED_TOKEN = '🔒'
const DISABLED_TOKEN_BYTES = 2

app.registerExtension({
    name: 'comfy.sp_nodes.prompt_checker',

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if(nodeData.name == 'PromptChecker'){
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                onNodeCreated && onNodeCreated.call(this);
                const prompt =  this.widgets[0];
                
                let token_div = $el("div", {
                    id: "token-buttons"
                });
                
                function tokenize(str) {
                    const tokens = [];
                    let currentToken = '';
                    let insideBrackets = 0;
                    let insideParentheses = false;

                    for (let i = 0; i < str.length; i++) {
                        const char = str[i];
                        
                        if (char === '{') {
                            insideBrackets++;
                            currentToken += char;
                        } else if (char === '}') {
                            insideBrackets--;
                            currentToken += char;
                        } else if (char === '(') {
                            insideParentheses = true;
                            currentToken += char;
                        } else if (char === ')') {
                            insideParentheses = false;
                            currentToken += char;
                        } else if (char === ',' && insideBrackets === 0 && !insideParentheses) {
                            tokens.push(currentToken.trim());
                            currentToken = '';
                        } else {
                            currentToken += char;
                        }
                    }

                    if (currentToken) {
                        tokens.push(currentToken.trim());
                    }

                    return tokens.filter(token => token);
                }

                function toggleToken(token, button) {
                    let currentTokens = tokenize(prompt.value); //prompt.value.split(',').map(t => t.trim()).filter(t => t);
                    
                    for (let i = 0; i < currentTokens.length; i++) {
                        if (currentTokens[i] === token) {
                            if (token.startsWith(DISABLED_TOKEN)) {
                                token = token.slice(DISABLED_TOKEN_BYTES);
                                button.style.backgroundColor = 'green';
                            } else {
                                token = `${DISABLED_TOKEN}${token}`;
                                button.style.backgroundColor = 'gray';
                            }
                            currentTokens[i] = token;
                        }
                    }

                    prompt.value = currentTokens.join(', ');
                }

                function adjustWeight(token, event) {
                    if (token.startsWith(DISABLED_TOKEN)) {
                        return token;
                    }
                
                    let currentTokens = tokenize(prompt.value);
                    const weightRegex = /^\((.*?):([0-9.]+)\)$/;
                
                    currentTokens = currentTokens.map(currentToken => {
                        let newToken = token
                        if (currentToken === token) {
                            let weightChange = event.deltaY < 0 ? 0.05 : -0.05;
                            if (weightRegex.test(token)) {
                                newToken = token.replace(weightRegex, (match, content, weight) => {
                                    let newWeight = parseFloat(weight) + weightChange;
                                    newWeight = Math.max(0.05, newWeight); // Prevent negative weight
                                    return newWeight !== 1.0 ? `(${content}:${newWeight.toFixed(2)})` : content;
                                });
                            } else {
                                let newWeight = weightChange > 0 ? 1.05 : 0.95;
                                newToken = `(${token}:${newWeight})`;
                            }
                        }
                        return currentToken === token ? newToken : currentToken;
                    });
                
                    prompt.value = currentTokens.join(', ');
                }
                

                function updateTokens() {
                    const tokens = tokenize(prompt.value); //prompt.value.split(',').map(t => t.trim()).filter(t => t);

                    // Create buttons for each token
                    while (token_div.firstChild) {
                        token_div.removeChild(token_div.firstChild);
                    }
                    tokens.forEach(token => {
                        let button = $el("button", {
                            type: "button",
                            textContent: token.startsWith(DISABLED_TOKEN) ? token.slice(DISABLED_TOKEN_BYTES) : token,
                            style: {
                                color: 'white'
                            },
                            onclick: () => toggleToken(token, button),
                            onwheel: (event) => adjustWeight(token, event)
                        });

                        if (token.startsWith(DISABLED_TOKEN)) {
                            button.style.backgroundColor = 'gray';
                        } else {
                            button.style.backgroundColor = 'green';
                        }

                        token_div.appendChild(button)
                    });
                }

                prompt.callback = async()=>{
                    updateTokens();
                }
                
                this.addDOMWidget('values',"buttons",token_div)

                return onNodeCreated;
            }
        }
    }
})