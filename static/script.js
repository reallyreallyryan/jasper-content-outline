// Jasper's Frontend Brain
let jasperStatus = 'unknown';
let generatedContent = null;

// Check Jasper's status when page loads
document.addEventListener('DOMContentLoaded', function() {
    checkJasperStatus();
});

async function checkJasperStatus() {
    try {
        const response = await fetch('/jasper-status');
        const data = await response.json();
        
        jasperStatus = data.status;
        const statusElement = document.getElementById('status-text');
        const statusIndicator = document.getElementById('status-indicator');
        
        if (data.status === 'ready') {
            statusElement.textContent = '🟢 Jasper is ready!';
            statusIndicator.className = 'status-indicator';
        } else {
            statusElement.textContent = '🔴 API key needed';
            statusIndicator.className = 'status-indicator error';
        }
    } catch (error) {
        console.error('Error checking Jasper status:', error);
        document.getElementById('status-text').textContent = '🔴 Connection error';
    }
}

async function generateContent() {
    const blogTopic = document.getElementById('blogTopic').value.trim();
    
    if (!blogTopic) {
        alert('Jasper needs a blog topic to work with! 🤖');
        return;
    }
    
    // Update UI for loading state
    const generateBtn = document.getElementById('generateBtn');
    const btnText = document.getElementById('btnText');
    const loader = document.getElementById('loader');
    
    generateBtn.disabled = true;
    btnText.textContent = 'Jasper is thinking...';
    loader.classList.remove('hidden');
    
    // Hide previous output
    document.getElementById('output-container').classList.add('hidden');
    
    try {
        const requestData = {
            blog_topic: blogTopic,
            client_name: document.getElementById('clientName').value,
            specialty: document.getElementById('specialty').value,
            location: document.getElementById('location').value
        };
        
        const response = await fetch('/generate-content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            generatedContent = data.content;
            displayContent(data.content, data.message);
        } else {
            alert(`Jasper encountered an issue: ${data.error}`);
        }
        
    } catch (error) {
        console.error('Error generating content:', error);
        alert('Jasper seems to be having connection issues. Check the console for details.');
    } finally {
        // Reset button state
        generateBtn.disabled = false;
        btnText.textContent = 'Let Jasper Work His Magic ✨';
        loader.classList.add('hidden');
    }
}

// UPDATE FOR static/script.js - Replace the displayContent function

function displayContent(content, message) {
    const outputContainer = document.getElementById('output-container');
    const contentOutput = document.getElementById('content-output');
    
    let html = `
        <div class="success-message" style="background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            ${message}
        </div>
        
        <!-- Blog Assignment Template -->
        <div class="blog-assignment-template" style="background: white; border: 2px solid #667eea; border-radius: 10px; overflow: hidden; margin-bottom: 25px;">
            <div style="background: #667eea; color: white; padding: 15px; text-align: center;">
                <h3 style="margin: 0; font-size: 1.2rem;">📋 BLOG ASSIGNMENT</h3>
            </div>
            
            <div class="assignment-table" style="display: grid; grid-template-columns: 150px 1fr; border-collapse: collapse;">
                <div style="background: #4a90e2; color: white; padding: 12px; font-weight: 600; border-bottom: 1px solid #ddd;">Title:</div>
                <div style="padding: 12px; border-bottom: 1px solid #ddd;">${content.title}</div>
                
                <div style="background: #4a90e2; color: white; padding: 12px; font-weight: 600; border-bottom: 1px solid #ddd;">Meta:</div>
                <div style="padding: 12px; border-bottom: 1px solid #ddd;">${content.meta}</div>
                
                <div style="background: #4a90e2; color: white; padding: 12px; font-weight: 600; border-bottom: 1px solid #ddd;">Primary Keywords:</div>
                <div style="padding: 12px; border-bottom: 1px solid #ddd;">${content.primaryKeywords}</div>
                
                <div style="background: #4a90e2; color: white; padding: 12px; font-weight: 600; border-bottom: 1px solid #ddd;">Keywords:</div>
                <div style="padding: 12px; border-bottom: 1px solid #ddd;">${content.keywords.join(', ')}</div>
                
                <div style="background: #4a90e2; color: white; padding: 12px; font-weight: 600; border-bottom: 1px solid #ddd;">CTA:</div>
                <div style="padding: 12px; border-bottom: 1px solid #ddd;">${content.cta}</div>
                
                <div style="background: #4a90e2; color: white; padding: 12px; font-weight: 600;">Resources:</div>
                <div style="padding: 12px;">
                    <ul style="margin: 0; padding-left: 20px;">
                        ${content.resources.map(resource => `<li>${resource}</li>`).join('')}
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Content Structure -->
        <div class="content-structure" style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
            <h3 style="margin-bottom: 15px;">📝 Content Structure</h3>
            
            <div style="margin-bottom: 15px;">
                <div style="font-weight: 600; font-size: 1.1rem; color: #333; margin-bottom: 5px;">H1: ${content.h1}</div>
            </div>
            
            ${content.h2Sections.map((section, index) => `
                <div style="margin-bottom: 15px; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #28a745;">
                    <div style="font-weight: 600; color: #333; margin-bottom: 8px;">H2: ${section.heading}</div>
                    <div style="color: #666; font-size: 0.9rem; margin-left: 20px;">
                        <strong>H3: Content</strong><br>
                        ${section.h3Content}
                    </div>
                </div>
            `).join('')}
        </div>
        
        <!-- Technical Details -->
        <div class="technical-details" style="background: #fff3cd; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
            <h3 style="margin-bottom: 15px;">⚙️ Technical SEO Details</h3>
            <div style="margin-bottom: 10px;"><strong>URL Slug:</strong> ${content.url}</div>
        </div>
    `;
    
    if (content.jasperNotes) {
        html += `
            <div class="jasper-notes" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px;">
                <h3 style="margin-bottom: 15px;">🤖 Jasper's Strategic Insights</h3>
                <p style="margin: 0; line-height: 1.6;">${content.jasperNotes}</p>
            </div>
        `;
    }
    
    contentOutput.innerHTML = html;
    outputContainer.classList.remove('hidden');
    
    // Smooth scroll to output
    outputContainer.scrollIntoView({ behavior: 'smooth' });
}

// Also update the download function to match the new format
function downloadContent() {
    if (!generatedContent) {
        alert('No content to download yet! Generate some content first.');
        return;
    }
    
    const content = `
JASPER'S BLOG ASSIGNMENT
Generated on: ${new Date().toLocaleDateString()}

======================
BLOG ASSIGNMENT TEMPLATE
======================
Title: ${generatedContent.title}
Meta: ${generatedContent.meta}
Primary Keywords: ${generatedContent.primaryKeywords}
Keywords: ${generatedContent.keywords.join(', ')}
CTA: ${generatedContent.cta}
Resources: ${generatedContent.resources.join(' | ')}

======================
CONTENT STRUCTURE
======================
H1: ${generatedContent.h1}

${generatedContent.h2Sections.map(section => `
H2: ${section.heading}
H3: Content
${section.h3Content}
`).join('\n')}

======================
TECHNICAL DETAILS
======================
URL: ${generatedContent.url}

${generatedContent.jasperNotes ? `
======================
JASPER'S INSIGHTS
======================
${generatedContent.jasperNotes}
` : ''}

---
Generated by Jasper 🤖 - Your SEO Assistant
    `;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jasper-blog-assignment-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadContent() {
    if (!generatedContent) {
        alert('No content to download yet! Generate some content first.');
        return;
    }
    
    const content = `
JASPER'S SEO CONTENT OUTLINE
Generated on: ${new Date().toLocaleDateString()}

======================
SEO METADATA
======================
Title Tag: ${generatedContent.titleTag}
Meta Description: ${generatedContent.metaDescription}
URL: ${generatedContent.url}
H1: ${generatedContent.h1}

======================
CONTENT OUTLINE
======================

${generatedContent.outline.map(section => `
${section.h2.toUpperCase()}
${'-'.repeat(section.h2.length)}
${section.content}

`).join('')}

======================
SEO STRATEGY NOTES
======================
${generatedContent.seoNotes.map(note => `• ${note}`).join('\n')}

${generatedContent.jasperNotes ? `
======================
JASPER'S INSIGHTS
======================
${generatedContent.jasperNotes}
` : ''}

---
Generated by Jasper 🤖 - Your SEO Assistant
    `;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jasper-seo-outline-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}