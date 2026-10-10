import { test, expect } from '@playwright/test';

test.describe('TaskForge Authentication & Kanban Flow', () => {
  test('User can log in and transition task state', async ({ page }) => {
    const baseURL = process.env.PLAYWRIGHT_TEST_BASE_URL || 'https://app.taskforge.dev';

    // 1. Visit Login Page
    await page.goto(`${baseURL}/login`);

    // 2. Fill Auth Credentials
    await page.fill('input[name="email"]', 'dev@taskforge.dev');
    await page.fill('input[name="password"]', 'SecurePassword123!');
    await page.click('button[type="submit"]');

    // 3. Verify Dashboard Redirection
    await expect(page).toHaveURL(`${baseURL}/dashboard`);
    await expect(page.locator('h1')).toContainText('Project Boards');

    // 4. Update Task Status via Dropdown
    const taskCard = page.locator('div', { hasText: 'Implement Auth Pipeline' });
    await taskCard.locator('select').selectOption('in_progress');

    // 5. Assert UI Persistence
    await expect(taskCard.locator('select')).toHaveValue('in_progress');
  });
});
