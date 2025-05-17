// Initialize CodeMirror editor
const editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
    mode: 'python',
    theme: 'monokai',
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    lineWrapping: true,
    matchBrackets: true,
    autoCloseBrackets: true
});

// Set initial example code
editor.setValue(`def hello(name):
    print("Hello,", name)
    return name

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return hello(self.name)

# Create a person object
person = Person("Alice", 30)
result = person.greet()`);

// Handle analyze button click
document.getElementById('analyze-btn').addEventListener('click', async () => {
    const code = editor.getValue();
    const astOutput = document.getElementById('ast-output');
    const irOutput = document.getElementById('ir-output');
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    const errorMessage = document.getElementById('error-message');

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
        });

        const result = await response.json();

        if (result.success) {
            // Update AST output
            astOutput.textContent = result.ast.join('\n');
            
            // Update IR output
            irOutput.textContent = result.ir.join('\n');
        } else {
            // Show error in modal
            errorMessage.textContent = result.error;
            errorModal.show();
        }
    } catch (error) {
        // Show error in modal
        errorMessage.textContent = 'An error occurred while processing the code.';
        errorModal.show();
    }
});

// Add keyboard shortcut (Ctrl+Enter) to analyze code
editor.setOption('extraKeys', {
    'Ctrl-Enter': () => {
        document.getElementById('analyze-btn').click();
    }
}); 