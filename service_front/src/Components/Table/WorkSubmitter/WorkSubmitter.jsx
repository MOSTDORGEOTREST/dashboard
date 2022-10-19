import React, { useState, useContext, useEffect } from 'react'
import axios from 'axios'

import './WorkSubmitter.css'

import SearchBar from '../../SearchBar/SearchBar'

import Context from '../../../context'

export default function WorkSubmitter({ searchData, isMobileType = false }) {
	const {
		api,
		newShow,
		accountData,
		setNewShow,
		setTable,
		setReloadData,
		inputDate,
		setInputDate,
		inputType,
		setInputType,
		inputCategory,
		setInputCategory,
		inputID,
		setInputID,
		inputCount,
		setInputCount,
		inputAdditional,
		setInputAdditional,
		editMode,
		setEditMode,
		workID,
		setWorkID,
	} = useContext(Context)

	// Блок повторной отправки
	const [sbmtPressed, setSbmtPressed] = useState(false)

	// Данные из заполняемых ячеек в таблице
	// const [inputDate, setInputDate] = useState(new Date().toJSON().slice(0, 10))
	// const [inputType, setInputType] = useState('')
	// const [inputCategory, setInputCategory] = useState('')
	// const [inputID, setInputID] = useState(-1)
	// const [inputCount, setInputCount] = useState('')
	// const [inputAdditional, setInputAdditional] = useState('')

	// Флаг ошибка исообщение с ошибкой
	const [isError, setIsError] = useState(false)
	const [errorText, setErrorText] = useState('')

	function clear() {
		setInputDate(new Date().toJSON().slice(0, 10))
		setInputType('')
		setInputCategory('')
		setInputID(-1)
		setInputCount('')
		setInputAdditional('')
		setNewShow(false)
		setWorkID(-1)

		setEditMode(false)
	}
	// useEffect(() => {
	// 	console.log(inputType)
	// }, [inputType])

	useEffect(() => {
		const _result = searchData.filter((item) => item.name === inputType)
		if (_result.length === 1) {
			setInputCategory(_result[0].position)
			setInputID(_result[0].id)
			return
		}
		setInputCategory('')
	}, [inputType])

	function onSubmitClick(event) {
		event.preventDefault()
		event.stopPropagation()

		if (sbmtPressed) return
		setSbmtPressed(true)

		const postNewData = axios.create()
		postNewData.interceptors.request.use(
			(config) => {
				// Код, необходимый до отправки запроса
				config.method = 'post'
				config.headers = { 'Content-Type': 'application/json' }
				config.withCredentials = true
				return config
			},
			(error) => {
				// Обработка ошибки из запроса
				return Promise.reject(error)
			}
		)
		postNewData.interceptors.response.use(
			function(response) {
				return response
			},
			function(error) {
				// Do something with response error
				if (error.response.status === 401) {
					submitError('Ошибка при отправке данных')
				}
				return { data: null }
			}
		)

		const _result = searchData.filter((item) => item.name === inputType)

		if (_result.length !== 1) {
			submitError('Выберите тип отчета из списка')
			return
		}
		if (inputID < 0) {
			submitError('Проверьте корректность данных')
			return
		}
		if (
			inputDate === '' ||
			inputType === '' ||
			inputCount === '' ||
			inputAdditional === ''
		) {
			submitError('Пожалуйста, заполните все поля')
			return
		}

		// console.log(accountData);
		postNewData
			.post(`${api}works/`, {
				user_id: accountData.id,
				date: inputDate,
				object_number: inputAdditional,
				work_id: inputID,
				count: inputCount,
			})
			.then((response) => {
				if (response.status === 200) {
					clear()
					return false
				}
				submitError(response.status)
				return true
			})
			.then((isError) => {
				if (!isError) {
					setReloadData(true)
					setTable()
				}
			})
			.then(() => setSbmtPressed(false))
	}

	function submitError(text) {
		setErrorText(text)
		setIsError(true)
		setTimeout(() => {
			setIsError(false)
			setErrorText('')
			setSbmtPressed(false)
		}, 1000)
	}

	function onEditClick(event) {
		event.preventDefault()
		event.stopPropagation()

		if (sbmtPressed) return
		setSbmtPressed(true)

		const postNewData = axios.create()
		postNewData.interceptors.request.use(
			(config) => {
				// Код, необходимый до отправки запроса
				config.method = 'put'
				config.headers = { 'Content-Type': 'application/json' }
				config.withCredentials = true
				return config
			},
			(error) => {
				// Обработка ошибки из запроса
				return Promise.reject(error)
			}
		)
		postNewData.interceptors.response.use(
			function(response) {
				return response
			},
			function(error) {
				// Do something with response error
				if (error.response.status === 401) {
					submitError('Ошибка при отправке данных')
				}
				return { data: null }
			}
		)

		const _result = searchData.filter((item) => item.name === inputType)

		if (_result.length !== 1) {
			submitError('Выберите тип отчета из списка')
			return
		}
		if (inputID < 0) {
			submitError('Проверьте корректность данных')
			return
		}
		if (
			inputDate === '' ||
			inputType === '' ||
			inputCount === '' ||
			inputAdditional === ''
		) {
			submitError('Пожалуйста, заполните все поля')
			return
		}
		if (workID < 0) {
			submitError('Работа не найдена в базе')
			return
		}

		postNewData
			.put(`${api}works/?id=${workID}`, {
				user_id: accountData.id,
				date: inputDate,
				object_number: inputAdditional,
				work_id: inputID,
				count: inputCount,
			})
			.then((response) => {
				if (response.status === 200) {
					clear()
					return false
				}
				submitError(response.status)
				return true
			})
			.then((isError) => {
				if (!isError) {
					setReloadData(true)
					setTable()
				}
			})
			.then(() => setSbmtPressed(false))
	}

	return isMobileType ? (
		// МОБИЛЬНАЯ ВЕРСИЯ, ИСПОЛЬЗУЕТСЯ ВНЕ! ТАБЛИЦЫ
		<div className={`mobile-sbmtr__wrapper ${isError ? 'error' : ''}`}>
			<h3>Добавление записи</h3>
			<div className="mobile-sbmtr__input">
				<label htmlFor="date">Дата</label>
				<input
					className="dynamic-table__input"
					type="date"
					name="date"
					value={inputDate}
					onChange={(event) => setInputDate(event.target.value)}
				/>
			</div>

			<div className="mobile-sbmtr__input">
				<label htmlFor="search">Тип</label>
				<Context.Provider value={{ inputType, setInputType }}>
					<SearchBar data={searchData} />
				</Context.Provider>
			</div>

			<div className="mobile-sbmtr__input">
				<label htmlFor="category">Категория</label>

				<input
					className="dynamic-table__input"
					disabled={true}
					type="text"
					name="category"
					placeholder="Автоматически"
					value={inputCategory}
				/>
			</div>

			<div className="mobile-sbmtr__input">
				<label htmlFor="count">Количество</label>

				<input
					className="dynamic-table__input"
					type="number"
					placeholder="Количество"
					name="count"
					value={inputCount}
					onChange={(event) => setInputCount(event.target.value)}
				/>
			</div>

			<div className="mobile-sbmtr__input">
				<label htmlFor="additional">Дополнительно</label>
				<input
					className="dynamic-table__input"
					type="text"
					placeholder="Номер объека и т.п. ..."
					name="additional"
					value={inputAdditional}
					onChange={(event) => setInputAdditional(event.target.value)}
				/>
			</div>

			<div className="dynamic-table__btns">
				<button
					className="dynamic-table__btn_cancel"
					onClick={() => {
						clear()
					}}
				>
					Отмена
				</button>
				<button
					type="submit"
					className="dynamic-table__btn_submit"
					onClick={(e) => {
						if (!editMode) {
							onSubmitClick(e)
							return
						}
						if (editMode) {
							onEditClick(e)
							return
						}
					}}
				>
					Сохранить
				</button>
				{isError ? (
					<div className="dynamic-table__error">{errorText}</div>
				) : null}
			</div>
		</div>
	) : (
		// ОБЫЧНАЯ ВЕРСИЯ, ИСПОЛЬЗУЕТСЯ ВНУТРИ ТАБЛИЦЫ
		<>
			<tr
				className={
					newShow
						? `dynamic-table__row dynamic-table__add-row dynamic-table__add-row_show ${
								isError ? 'error' : ''
						  }`
						: 'dynamic-table__row dynamic-table__add-row'
				}
			>
				<td>
					<input
						className="dynamic-table__input"
						type="date"
						value={inputDate}
						onChange={(event) => setInputDate(event.target.value)}
					/>
				</td>
				<td>
					<Context.Provider value={{ inputType, setInputType }}>
						<SearchBar data={searchData} />
					</Context.Provider>
				</td>
				<td>
					<input
						className="dynamic-table__input"
						disabled={true}
						type="text"
						placeholder="Автоматически"
						value={inputCategory}
					/>
				</td>
				<td>
					<input
						className="dynamic-table__input"
						type="number"
						placeholder="Количество"
						value={inputCount}
						min={1}
						onChange={(event) => setInputCount(event.target.value)}
					/>
				</td>
				<td>
					<input
						className="dynamic-table__input"
						type="text"
						placeholder="Номер объека и т.п. ..."
						value={inputAdditional}
						onChange={(event) => setInputAdditional(event.target.value)}
					/>
				</td>
			</tr>
			<tr
				className={
					newShow
						? 'dynamic-table__row dynamic-table__add-row dynamic-table__add-row_bottom dynamic-table__add-row_show'
						: 'dynamic-table__row dynamic-table__add-row'
				}
			>
				<td></td>
				<td></td>
				<td></td>
				<td>
					{isError ? (
						<div className="dynamic-table__error">{errorText}</div>
					) : null}
				</td>
				<td>
					<div className="dynamic-table__btns">
						<button
							className="dynamic-table__btn_cancel"
							onClick={() => {
								clear()
								setNewShow(false)
							}}
						>
							Отмена
						</button>
						<button
							className="dynamic-table__btn_submit"
							onClick={(e) => {
								if (!editMode) {
									onSubmitClick(e)
									return
								}
								if (editMode) {
									onEditClick(e)
									return
								}
							}}
							type="submit"
						>
							Сохранить
						</button>
					</div>
				</td>
			</tr>
		</>
	)
}
