from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.Horarios import esquemas, modelos


# ==========================================
# 1. FUNCIONES AUXILIARES (Logica de Tiempo)
# ==========================================

def parse_hora_a_minutos(hora_str: str) -> int:
    """
    Convierte "HH:MM" a minutos totales.
    Ejemplo: "07:30" -> 450.
    """
    try:
        horas, minutos = map(int, hora_str.split(':'))
        return horas * 60 + minutos
    except ValueError:
        return 0


def validar_choques(items: List[esquemas.ItemCreate]):
    """
    Verifica traslapes considerando el DIA de la semana.
    Formato esperado: "Lunes 07:00 - 08:30"
    """
    # Lista temporal: [(dia, inicio, fin, materia_id), ...]
    intervalos = []

    for item in items:
        if not item.hora_grupo or "-" not in item.hora_grupo:
            continue

        try:
            # 1. Separar el rango: "Lunes 07:00" y "08:30"
            partes_rango = item.hora_grupo.split("-")
            parte_izquierda = partes_rango[0].strip() # "Lunes 07:00"
            hora_fin_str = partes_rango[1].strip()    # "08:30"

            # 2. Separar Día y Hora de inicio
            # Dividimos por espacios. El último elemento es la hora, el resto es el día
            datos_inicio = parte_izquierda.split(" ")
            
            if len(datos_inicio) < 2:
                # Si no tiene formato "Dia Hora", saltamos validación (o lanzamos error)
                continue
                
            hora_inicio_str = datos_inicio[-1] # "07:00"
            # Unimos el resto por si el día fuera compuesto (ej. no aplica aquí pero es seguro)
            dia = " ".join(datos_inicio[:-1])  # "Lunes"

            # 3. Convertir a minutos
            start_min = parse_hora_a_minutos(hora_inicio_str)
            end_min = parse_hora_a_minutos(hora_fin_str)

            if start_min >= end_min:
                # Caso raro: hora inicio mayor que fin
                continue

            # 4. Validar contra intervalos EXISTENTES
            for (ex_dia, ex_start, ex_end, ex_id) in intervalos:
                # SOLO COMPARAMOS SI ES EL MISMO DÍA
                if ex_dia == dia:
                    # Lógica de colisión: (InicioA < FinB) y (InicioB < FinA)
                    if start_min < ex_end and ex_start < end_min:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(
                                f"Choque de horario el {dia}: La materia "
                                f"(ID {item.materia_id}) se cruza con otra materia existente."
                            )
                        )

            # Si no hubo choque, guardamos este intervalo
            intervalos.append((dia, start_min, end_min, item.materia_id))

        except HTTPException as e:
            raise e
        except Exception as e:
            print(f"Error validando item {item}: {e}")
            continue


# ==========================================
# 2. FUNCIONES CRUD PRINCIPALES
# ==========================================

def get_my_horarios(db: Session, user_id: int):
    return db.query(modelos.Horario).filter(
        modelos.Horario.user_id == user_id
    ).all()


def create_horario(
    db: Session,
    horario: esquemas.HorarioCreate,
    user_id: int
):
    # --- PASO 0: VALIDAR CHOQUES ---
    validar_choques(horario.items)

    try:
        # 1. Crear cabecera
        db_horario = modelos.Horario(
            nombre=horario.nombre,
            user_id=user_id
        )
        db.add(db_horario)
        db.flush()

        # 2. Agregar items
        for item in horario.items:
            db_item = modelos.ItemHorario(
                horario_id=db_horario.id,
                materia_id=item.materia_id,
                hora_grupo=item.hora_grupo
            )
            db.add(db_item)

        # 3. Commit
        db.commit()
        db.refresh(db_horario)
        return db_horario

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        print(f"Error creando horario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al guardar el horario."
        )


def delete_horario(db: Session, horario_id: int, user_id: int) -> bool:
    horario = db.query(modelos.Horario).filter(
        modelos.Horario.id == horario_id,
        modelos.Horario.user_id == user_id
    ).first()

    if horario:
        db.delete(horario)
        db.commit()
        return True

    return False