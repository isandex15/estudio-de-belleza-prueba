import { existsSync, mkdirSync, rmSync, rmdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from './auth';

const carpetaBackups = resolve(__dirname, '../../../static/backups');

test('mostrar las opciones de mantenimiento', async ({ page }) => {
  // CP-MAN-16: Muestra las opciones de mantenimiento.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Mantenimiento.
  await abrirModulo(page, 'mantenimiento');

  // 3. Verificar las opciones y el formato de restauración.
  await expect(page.locator('#table1')).toBeVisible();
  await expect(page.locator('#btnCrearBackup')).toBeVisible();
  await expect(page.locator('#formRestaurarBackup input[name="backup_file"]'))
    .toHaveAttribute('accept', '.sql');
});

test('rechazar restaurar un archivo que no es SQL', async ({ page }) => {
  // CP-MAN-17: Rechaza restaurar un archivo que no es SQL.

  const carpetaExistia = existsSync(carpetaBackups);
  mkdirSync(carpetaBackups, { recursive: true });
  const archivoListado = `playwright_ui_${Date.now()}_${Math.random()
    .toString(16)
    .slice(2)}.sql`;

  try {
    writeFileSync(
      join(carpetaBackups, archivoListado),
      '-- archivo temporal de prueba\n'
    );

    // 1. Iniciar sesión.
    await iniciarSesion(page);

    // 2. Acceder al módulo Mantenimiento.
    await abrirModulo(page, 'mantenimiento');

    // 3. Abrir el formulario de restauración.
    const filaBackup = page.locator('#table1 tbody tr').filter({
      hasText: archivoListado,
    });
    await expect(filaBackup).toHaveCount(1);
    await filaBackup.getByRole('button', { name: 'Restaurar' }).click();

    const modal = page.locator('#modalRestaurarBackup');
    await expect(modal).toBeVisible();

    // 4. Enviar un archivo con extensión no permitida.
    await modal.locator('input[name="backup_file"]').setInputFiles({
      name: 'respaldo_invalido.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('no es un respaldo SQL'),
    });
    await modal.getByRole('button', { name: 'Guardar' }).click();

    // 5. Comprobar el mensaje de rechazo.
    await expect(page.locator('.swal2-popup')).toContainText(
      'No se pudo restaurar.',
      { timeout: 15000 }
    );
  } finally {
    if (existsSync(join(carpetaBackups, archivoListado))) {
      rmSync(join(carpetaBackups, archivoListado));
    }
    if (!carpetaExistia && existsSync(carpetaBackups)) {
      rmdirSync(carpetaBackups);
    }
  }
});
