// Email Template Utilities for Base10

export interface WelcomeEmailProps {
  userName: string
  userRole: 'student' | 'teacher' | 'parent'
  verificationUrl: string
}

export interface VerificationEmailProps {
  userName: string
  verificationUrl: string
}

export interface WeeklyReportEmailProps {
  userName: string
  stats: {
    questionsAnswered: number
    accuracy: number
    studyMinutes: number
    topSubjects: Array<{ name: string; accuracy: number }>
    improvementAreas: Array<{ name: string; accuracy: number }>
  }
  dashboardUrl: string
}

// Base10 Brand Colors
const colors = {
  primary: '#10b981', // emerald-500
  secondary: '#8b5cf6', // purple-500
  dark: '#1e293b', // slate-800
  light: '#f8fafc', // slate-50
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
}

// Email Base Styles
const baseStyles = `
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #334155;
    background-color: #f8fafc;
    margin: 0;
    padding: 0;
  }
  .container {
    max-width: 600px;
    margin: 0 auto;
    background-color: #ffffff;
  }
  .header {
    background: linear-gradient(135deg, #10b981 0%, #8b5cf6 100%);
    padding: 40px 20px;
    text-align: center;
  }
  .logo {
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .content {
    padding: 40px 30px;
  }
  .button {
    display: inline-block;
    padding: 16px 32px;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: #ffffff !important;
    text-decoration: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 16px;
    margin: 20px 0;
    box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
  }
  .footer {
    background-color: #f1f5f9;
    padding: 30px;
    text-align: center;
    font-size: 14px;
    color: #64748b;
  }
  .feature-list {
    background-color: #f8fafc;
    border-left: 4px solid #10b981;
    padding: 20px;
    margin: 20px 0;
    border-radius: 8px;
  }
  .stat-card {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    margin: 10px 0;
  }
`

export function getWelcomeEmail({ userName, userRole, verificationUrl }: WelcomeEmailProps): string {
  const roleContent = {
    student: {
      title: 'Welcome to Your Learning Journey! 🎓',
      message: 'Get ready to ace your WAEC exams with 700+ practice questions, AI-powered explanations, and smart progress tracking.',
      steps: [
        '✅ Verify your email address',
        '📝 Complete your student profile',
        '🎯 Take your first practice quiz',
      ],
    },
    teacher: {
      title: 'Welcome to Your Teaching Dashboard! 👨‍🏫',
      message: 'Empower your students with Base10\'s comprehensive learning platform. Create classrooms, track progress, and drive results.',
      steps: [
        '✅ Verify your email address',
        '🏫 Set up your first classroom',
        '👥 Invite students to join',
      ],
    },
    parent: {
      title: 'Welcome to Base10! 👨‍👩‍👧',
      message: 'Stay connected with your child\'s learning journey. Monitor progress, receive weekly reports, and support their success.',
      steps: [
        '✅ Verify your email address',
        '👤 Complete your parent profile',
        '🔗 Link to your child\'s account',
      ],
    },
  }

  const content = roleContent[userRole]

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Welcome to Base10</title>
      <style>${baseStyles}</style>
    </head>
    <body>
      <div class="container">
        <!-- Header -->
        <div class="header">
          <h1 class="logo">Base10</h1>
          <p style="color: #d1fae5; margin: 10px 0 0 0; font-size: 14px;">Master Your WAEC Exams</p>
        </div>

        <!-- Content -->
        <div class="content">
          <h2 style="color: #1e293b; font-size: 24px; margin: 0 0 20px 0;">
            Hi ${userName},
          </h2>
          
          <h1 style="color: #10b981; font-size: 28px; margin: 0 0 20px 0; font-weight: 800;">
            ${content.title}
          </h1>

          <p style="font-size: 16px; color: #475569; margin: 0 0 30px 0;">
            ${content.message}
          </p>

          <!-- Verification CTA -->
          <div style="text-align: center; margin: 40px 0;">
            <a href="${verificationUrl}" class="button">
              Verify Your Email Address
            </a>
            <p style="font-size: 13px; color: #94a3b8; margin: 15px 0 0 0;">
              This link expires in 24 hours
            </p>
          </div>

          <!-- Getting Started -->
          <div class="feature-list">
            <h3 style="margin: 0 0 15px 0; color: #1e293b; font-size: 18px;">
              Get Started in 3 Steps:
            </h3>
            ${content.steps.map(step => `
              <p style="margin: 10px 0; font-size: 15px; color: #475569;">
                ${step}
              </p>
            `).join('')}
          </div>

          <!-- Features -->
          <h3 style="margin: 30px 0 20px 0; color: #1e293b; font-size: 18px;">
            What You'll Love:
          </h3>
          <ul style="list-style: none; padding: 0; margin: 0;">
            <li style="padding: 10px 0; border-bottom: 1px solid #e2e8f0;">
              📚 <strong>700+ Questions:</strong> Comprehensive WAEC coverage
            </li>
            <li style="padding: 10px 0; border-bottom: 1px solid #e2e8f0;">
              🤖 <strong>AI Tutor:</strong> Instant explanations when you need them
            </li>
            <li style="padding: 10px 0; border-bottom: 1px solid #e2e8f0;">
              📊 <strong>Smart Analytics:</strong> Track your progress & weak areas
            </li>
            <li style="padding: 10px 0;">
              📱 <strong>Offline-First:</strong> Study anytime, anywhere
            </li>
          </ul>

          <!-- Fallback Link -->
          <p style="font-size: 13px; color: #94a3b8; margin: 30px 0 0 0; padding: 20px; background-color: #f8fafc; border-radius: 8px;">
            <strong>Can't click the button?</strong><br>
            Copy and paste this link into your browser:<br>
            <span style="color: #10b981; word-break: break-all;">${verificationUrl}</span>
          </p>
        </div>

        <!-- Footer -->
        <div class="footer">
          <p style="margin: 0 0 15px 0;">
            <strong style="color: #1e293b;">Base10</strong><br>
            Empowering students to excel in WAEC exams
          </p>
          <p style="margin: 0 0 15px 0;">
            <a href="mailto:support@base10.app" style="color: #10b981; text-decoration: none;">support@base10.app</a>
          </p>
          <p style="margin: 0; font-size: 12px;">
            © 2025 Base10. All rights reserved.
          </p>
        </div>
      </div>
    </body>
    </html>
  `
}

export function getVerificationEmail({ userName, verificationUrl }: VerificationEmailProps): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Verify Your Email - Base10</title>
      <style>${baseStyles}</style>
    </head>
    <body>
      <div class="container">
        <!-- Header -->
        <div class="header">
          <h1 class="logo">Base10</h1>
        </div>

        <!-- Content -->
        <div class="content">
          <h2 style="color: #1e293b; font-size: 24px; margin: 0 0 20px 0;">
            Hi ${userName},
          </h2>
          
          <h1 style="color: #10b981; font-size: 28px; margin: 0 0 20px 0; font-weight: 800;">
            Verify Your Email Address
          </h1>

          <p style="font-size: 16px; color: #475569; margin: 0 0 30px 0;">
            We need to verify your email address to complete your Base10 account setup. Click the button below to verify:
          </p>

          <!-- Verification CTA -->
          <div style="text-align: center; margin: 40px 0;">
            <a href="${verificationUrl}" class="button">
              Verify Email Address
            </a>
            <p style="font-size: 13px; color: #94a3b8; margin: 15px 0 0 0;">
              ⏰ This link expires in 24 hours
            </p>
          </div>

          <!-- Security Notice -->
          <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; margin: 30px 0; border-radius: 8px;">
            <p style="margin: 0; font-size: 14px; color: #92400e;">
              <strong>🔒 Security Notice:</strong><br>
              If you didn't create a Base10 account, you can safely ignore this email.
            </p>
          </div>

          <!-- Fallback Link -->
          <p style="font-size: 13px; color: #94a3b8; margin: 30px 0 0 0; padding: 20px; background-color: #f8fafc; border-radius: 8px;">
            <strong>Can't click the button?</strong><br>
            Copy and paste this link into your browser:<br>
            <span style="color: #10b981; word-break: break-all;">${verificationUrl}</span>
          </p>
        </div>

        <!-- Footer -->
        <div class="footer">
          <p style="margin: 0 0 15px 0;">
            <strong style="color: #1e293b;">Base10</strong><br>
            Master Your WAEC Exams
          </p>
          <p style="margin: 0 0 15px 0;">
            <a href="mailto:support@base10.app" style="color: #10b981; text-decoration: none;">support@base10.app</a>
          </p>
          <p style="margin: 0; font-size: 12px;">
            © 2025 Base10. All rights reserved.
          </p>
        </div>
      </div>
    </body>
    </html>
  `
}

export function getWeeklyReportEmail({ userName, stats, dashboardUrl }: WeeklyReportEmailProps): string {
  const accuracyColor = stats.accuracy >= 80 ? '#10b981' : stats.accuracy >= 60 ? '#f59e0b' : '#ef4444'
  
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Your Weekly Progress - Base10</title>
      <style>${baseStyles}</style>
    </head>
    <body>
      <div class="container">
        <!-- Header -->
        <div class="header">
          <h1 class="logo">Base10</h1>
          <p style="color: #d1fae5; margin: 10px 0 0 0; font-size: 14px;">📊 Your Weekly Progress Report</p>
        </div>

        <!-- Content -->
        <div class="content">
          <h2 style="color: #1e293b; font-size: 24px; margin: 0 0 20px 0;">
            Hi ${userName},
          </h2>
          
          <p style="font-size: 16px; color: #475569; margin: 0 0 30px 0;">
            Here's how you performed this week. Keep up the great work!
          </p>

          <!-- Stats Grid -->
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 30px 0;">
            <div class="stat-card">
              <div style="font-size: 36px; font-weight: 800; margin: 0 0 5px 0;">${stats.questionsAnswered}</div>
              <div style="font-size: 14px; opacity: 0.9;">Questions Answered</div>
            </div>
            <div class="stat-card">
              <div style="font-size: 36px; font-weight: 800; margin: 0 0 5px 0;">${stats.accuracy}%</div>
              <div style="font-size: 14px; opacity: 0.9;">Overall Accuracy</div>
            </div>
          </div>

          <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: #ffffff; padding: 20px; border-radius: 12px; margin: 15px 0; text-align: center;">
            <div style="font-size: 36px; font-weight: 800; margin: 0 0 5px 0;">${stats.studyMinutes}</div>
            <div style="font-size: 14px; opacity: 0.9;">Minutes Studied</div>
          </div>

          <!-- Top Subjects -->
          <div style="margin: 30px 0;">
            <h3 style="color: #1e293b; font-size: 18px; margin: 0 0 15px 0;">
              🏆 Your Top Subjects:
            </h3>
            ${stats.topSubjects.map(subject => `
              <div style="background-color: #ecfdf5; border-left: 4px solid #10b981; padding: 15px; margin: 10px 0; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <strong style="color: #1e293b; font-size: 16px;">${subject.name}</strong>
                  <span style="color: #10b981; font-size: 20px; font-weight: 800;">${subject.accuracy}%</span>
                </div>
              </div>
            `).join('')}
          </div>

          <!-- Improvement Areas -->
          <div style="margin: 30px 0;">
            <h3 style="color: #1e293b; font-size: 18px; margin: 0 0 15px 0;">
              📈 Focus On These Areas:
            </h3>
            ${stats.improvementAreas.map(subject => `
              <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 10px 0; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <strong style="color: #1e293b; font-size: 16px;">${subject.name}</strong>
                  <span style="color: #f59e0b; font-size: 20px; font-weight: 800;">${subject.accuracy}%</span>
                </div>
              </div>
            `).join('')}
          </div>

          <!-- CTA -->
          <div style="text-align: center; margin: 40px 0;">
            <a href="${dashboardUrl}" class="button">
              View Full Dashboard
            </a>
          </div>
        </div>

        <!-- Footer -->
        <div class="footer">
          <p style="margin: 0 0 15px 0;">
            <strong style="color: #1e293b;">Base10</strong><br>
            Master Your WAEC Exams
          </p>
          <p style="margin: 0; font-size: 12px;">
            Weekly reports are sent every Sunday at 9:00 AM
          </p>
        </div>
      </div>
    </body>
    </html>
  `
}

// Plain text versions for email clients that don't support HTML

export function getPlainTextWelcome({ userName, userRole, verificationUrl }: WelcomeEmailProps): string {
  const roleContent = {
    student: {
      title: 'Welcome to Your Learning Journey!',
      steps: [
        '1. Verify your email address',
        '2. Complete your student profile',
        '3. Take your first practice quiz',
      ],
    },
    teacher: {
      title: 'Welcome to Your Teaching Dashboard!',
      steps: [
        '1. Verify your email address',
        '2. Set up your first classroom',
        '3. Invite students to join',
      ],
    },
    parent: {
      title: 'Welcome to Base10!',
      steps: [
        '1. Verify your email address',
        '2. Complete your parent profile',
        '3. Link to your child\'s account',
      ],
    },
  }

  const content = roleContent[userRole]

  return `
Base10 - Master Your WAEC Exams

Hi ${userName},

${content.title}

Get ready to ace your WAEC exams with Base10's comprehensive learning platform.

VERIFY YOUR EMAIL:
${verificationUrl}

(This link expires in 24 hours)

GET STARTED IN 3 STEPS:
${content.steps.join('\n')}

WHAT YOU'LL LOVE:
• 700+ Questions: Comprehensive WAEC coverage
• AI Tutor: Instant explanations when you need them
• Smart Analytics: Track your progress & weak areas
• Offline-First: Study anytime, anywhere

---
Base10
support@base10.app
© 2025 Base10. All rights reserved.
  `.trim()
}
