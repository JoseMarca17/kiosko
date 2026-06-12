from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
        ('usuarios', '0001_initial'),
        ('catalogo', '0001_initial'),
        ('pedidos', '0001_initial'),
    ]

    operations = [
        # 1. SEEDS FOR ROLES
        migrations.RunSQL(
            sql="""
            INSERT INTO roles (id_rol, nombre, descripcion, activo) VALUES
            (1, 'admin', 'Administrador del sistema, acceso total', 1),
            (2, 'estudiante', 'Usuario estándar, puede hacer pedidos', 1),
            (3, 'staff_kiosko', 'Personal del kiosko, gestiona pedidos y stock', 1)
            ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), descripcion=VALUES(descripcion), activo=VALUES(activo);
            """,
            reverse_sql="DELETE FROM roles WHERE id_rol IN (1, 2, 3);"
        ),

        # 2. SEEDS FOR ESTADOS PEDIDO
        migrations.RunSQL(
            sql="""
            INSERT INTO estados_pedido (id_estado, nombre, descripcion, color_hex) VALUES
            (1, 'pendiente_pago', 'Pedido creado, esperando pago', '#FFA500'),
            (2, 'pendiente_validacion', 'Comprobante subido, esperando aprobación admin', '#FFD700'),
            (3, 'pagado', 'Pago validado y confirmado', '#4CAF50'),
            (4, 'preparando', 'Pedido en preparación en el kiosko', '#2196F3'),
            (5, 'listo', 'Pedido listo para recoger', '#00BCD4'),
            (6, 'entregado', 'Pedido entregado al estudiante', '#9C27B0'),
            (7, 'cancelado', 'Pedido cancelado', '#F44336')
            ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), descripcion=VALUES(descripcion), color_hex=VALUES(color_hex);
            """,
            reverse_sql="DELETE FROM estados_pedido WHERE id_estado IN (1, 2, 3, 4, 5, 6, 7);"
        ),

        # 3. SEEDS FOR CATEGORIAS
        migrations.RunSQL(
            sql="""
            INSERT INTO categorias (id_categoria, nombre, descripcion, orden, activo) VALUES
            (1, 'Bebidas', 'Jugos, gaseosas, agua y bebidas calientes', 1, 1),
            (2, 'Golosinas', 'Snacks, galletas, chocolates', 2, 1),
            (3, 'Comida', 'Sánguches, salteñas, hamburguesas', 3, 1),
            (4, 'Postres', 'Pasteles, gelatinas, tortas', 4, 1),
            (5, 'Otros', 'Misceláneos', 5, 1)
            ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), descripcion=VALUES(descripcion), orden=VALUES(orden), activo=VALUES(activo);
            """,
            reverse_sql="DELETE FROM categorias WHERE id_categoria IN (1, 2, 3, 4, 5);"
        ),

        # 4. VIEW: v_productos_mas_vendidos
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE VIEW v_productos_mas_vendidos AS
            SELECT
                p.id_producto,
                p.nombre,
                c.nombre             AS categoria,
                SUM(dp.cantidad)     AS unidades_vendidas,
                SUM(dp.subtotal)     AS ingresos_totales,
                COUNT(DISTINCT dp.id_pedido) AS veces_pedido
            FROM detalle_pedido dp
            JOIN productos      p  ON dp.id_producto = p.id_producto
            JOIN categorias     c  ON p.id_categoria = c.id_categoria
            JOIN pedidos        pe ON dp.id_pedido   = pe.id_pedido
            JOIN estados_pedido e  ON pe.id_estado   = e.id_estado
            WHERE e.nombre NOT IN ('cancelado', 'pendiente_pago', 'pendiente_validacion')
              AND pe.cancelado = 0
            GROUP BY p.id_producto, p.nombre, c.nombre
            ORDER BY unidades_vendidas DESC;
            """,
            reverse_sql="DROP VIEW IF EXISTS v_productos_mas_vendidos;"
        ),

        # 5. TRIGGER: trg_descontar_stock
        migrations.RunSQL(
            sql="""
            CREATE TRIGGER trg_descontar_stock
            AFTER UPDATE ON pedidos
            FOR EACH ROW
            BEGIN
                IF NEW.id_estado = (SELECT id_estado FROM estados_pedido WHERE nombre = 'pagado')
                   AND OLD.id_estado != NEW.id_estado THEN
                    UPDATE inventario i
                    INNER JOIN detalle_pedido dp ON dp.id_producto = i.id_producto
                    SET i.stock_actual = i.stock_actual - dp.cantidad,
                        i.ultima_actualizacion = CURRENT_TIMESTAMP
                    WHERE dp.id_pedido = NEW.id_pedido;
                END IF;
            END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS trg_descontar_stock;"
        ),

        # 6. TRIGGER: trg_restaurar_stock_cancelacion
        migrations.RunSQL(
            sql="""
            CREATE TRIGGER trg_restaurar_stock_cancelacion
            AFTER UPDATE ON pedidos
            FOR EACH ROW
            BEGIN
                IF NEW.cancelado = 1 AND OLD.cancelado = 0 THEN
                    IF OLD.id_estado = (SELECT id_estado FROM estados_pedido WHERE nombre = 'pagado') THEN
                        UPDATE inventario i
                        INNER JOIN detalle_pedido dp ON dp.id_producto = i.id_producto
                        SET i.stock_actual = i.stock_actual + dp.cantidad,
                            i.ultima_actualizacion = CURRENT_TIMESTAMP
                        WHERE dp.id_pedido = NEW.id_pedido;
                    END IF;
                END IF;
            END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS trg_restaurar_stock_cancelacion;"
        ),

        # 7. TRIGGER: trg_generar_codigo_pedido
        migrations.RunSQL(
            sql="""
            CREATE TRIGGER trg_generar_codigo_pedido
            BEFORE INSERT ON pedidos
            FOR EACH ROW
            BEGIN
                DECLARE contador INT;
                SELECT COUNT(*) + 1 INTO contador
                FROM pedidos
                WHERE DATE(fecha_pedido) = CURDATE();
                SET NEW.codigo_pedido = CONCAT(
                    'PED-',
                    DATE_FORMAT(CURDATE(), '%Y%m%d'),
                    '-',
                    LPAD(contador, 4, '0')
                );
            END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS trg_generar_codigo_pedido;"
        ),
    ]
