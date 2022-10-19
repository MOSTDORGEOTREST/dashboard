import React, { useState, useEffect, useContext } from 'react'

import axios from 'axios'

import './Table.css'

import WorkSubmitter from './WorkSubmitter/WorkSubmitter'
import Context from '../../context'
import useWindowDimensions from '../windowResizeHook'

export default function Table({ searchData }) {
	const { api, accountData, setReloadData } = useContext(Context)

	const [mobile, setMobile] = useState(false)

	const { width } = useWindowDimensions()

	const [newShow, setNewShow] = useState(false)

	const [works, setWorks] = useState([])

	const [tableDate, setTableDate] = useState('')
	const [tableFullDate, setTableFullDate] = useState(null)

	// Данные из заполняемых ячеек в таблице
	const [inputDate, setInputDate] = useState(new Date().toJSON().slice(0, 10))
	const [inputType, setInputType] = useState('')
	const [inputCategory, setInputCategory] = useState('')
	const [inputID, setInputID] = useState(-1)
	const [workID, setWorkID] = useState(-1)
	const [inputCount, setInputCount] = useState('')
	const [inputAdditional, setInputAdditional] = useState('')
	const [editMode, setEditMode] = useState(false)

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

	/**
	 * Обновляет дату для таблицы в формате мес. гггг. в `tableDate` и полную дату в `tableFullDate`
	 * @param {Date} date Полная дата
	 */
	function updateTableFullDate(date) {
		if (date) {
			setTableFullDate(date)
			const options = { year: 'numeric', month: 'short' }
			const formatdate = new Intl.DateTimeFormat('ru-RU', options)
				.format(date)
				.replace(' г.', '')
			setTableDate(formatdate)
		} else {
			setTableFullDate(null)
			setTableDate('')
		}
	}

	function setTable() {
		const tableRequestor = axios.create()
		tableRequestor.interceptors.request.use(
			(config) => {
				// Код, необходимый до отправки запроса
				config.method = 'get'
				config.withCredentials = true
				return config
			},
			(error) => {
				// Обработка ошибки из запроса
				return Promise.reject(error)
			}
		)
		tableRequestor.interceptors.response.use(
			function(response) {
				return response
			},
			function(error) {
				// Do something with response error
				if (error.response.status === 401) {
					console.log(error)
				}
				return { data: null }
			}
		)

		const currDate = new Date()
		let _date = tableFullDate
		if (!_date) {
			_date = currDate
		}

		tableRequestor
			.get(
				`${api}works/?month=${_date.getMonth() +
					1}&year=${_date.getFullYear()}&user_id=${accountData.id}`
			)
			.then((response) => {
				if (response.status === 200) {
					// [
					// 	{
					// 	  "id": 1,
					// 	  "date": "2022-10-06",
					// 	  "object_number": "111",
					// 	  "work_name": "Протокол python",
					// 	  "work_id": 1,
					// 	  "count": 1,
					// 	  "price": 30
					// 	}
					//   ]
					let data = response.data
					data.forEach((item) => {
						const _result = searchData.filter((i) => i.name === item.work_name)
						item['work_category'] = _result[0].position
						item['full_date'] = item.date

						const options = { year: 'numeric', month: 'short', day: 'numeric' }
						const formatDate = new Intl.DateTimeFormat('ru-RU', options)
							.format(new Date(item.date))
							.replace(' г.', '')
						item.date = formatDate
					})
					data = data.reverse()
					setWorks(data)
				}
			})
	}

	useEffect(() => {
		updateTableFullDate(new Date())
	}, [])

	useEffect(() => {
		setTable()
	}, [tableDate])

	function deleteWork(workID) {
		if (workID < 0) return
		const requestor = axios.create()
		requestor.interceptors.request.use(
			(config) => {
				// Код, необходимый до отправки запроса
				config.method = 'DELETE'
				config.withCredentials = true
				return config
			},
			(error) => {
				// Обработка ошибки из запроса
				console.log(error)
				return Promise.reject(error)
			}
		)
		requestor.interceptors.response.use(
			function(response) {
				return response
			},
			function(error) {
				// Do something with response error
				console.log(error)

				return { data: null }
			}
		)

		requestor.request(`${api}works/?id=${workID}`).then(() => {
			setTable()
			setReloadData(true)
		})
	}

	function changeWork(date, type, category, id, count, additional) {
		clear()

		setNewShow(true)
		setInputDate(date)
		setInputType(type)
		setInputCategory(category)
		setWorkID(id)
		setInputCount(count)
		setInputAdditional(additional)

		setEditMode(true)
	}

	const mobileWidth = 1155

	useEffect(() => {
		if (width <= mobileWidth) {
			if (!mobile) setMobile(true)
		} else {
			if (mobile) setMobile(false)
		}
	}, [width])

	return (
		<div className="card-item dynamic-table-item">
			<div className="dynamic-table__header">
				<h1>{`Выполненные работы за`}</h1>
				<div className="dynamic-table__header__buttons">
					<button
						onClick={() => {
							const date = tableFullDate
							date.setMonth(date.getMonth() - 1)
							updateTableFullDate(date)
						}}
					>
						<svg
							className="arrow-left"
							xmlns="http://www.w3.org/2000/svg"
							width="24"
							height="24"
						>
							<path d="M13.293 6.293 7.586 12l5.707 5.707 1.414-1.414L10.414 12l4.293-4.293z"></path>
						</svg>
					</button>
					<h1>{tableDate}</h1>
					<button
						onClick={() => {
							const date = tableFullDate
							date.setMonth(date.getMonth() + 1)
							updateTableFullDate(date)
						}}
						title=""
					>
						<svg
							className="arrow-right"
							xmlns="http://www.w3.org/2000/svg"
							width="24"
							height="24"
						>
							<path d="M10.707 17.707 16.414 12l-5.707-5.707-1.414 1.414L13.586 12l-4.293 4.293z"></path>
						</svg>
					</button>
				</div>
			</div>

			{mobile ? (
				<Context.Provider
					value={{
						api,
						accountData,
						newShow,
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
					}}
				>
					<WorkSubmitter
						searchData={searchData}
						isMobileType={true}
					></WorkSubmitter>
				</Context.Provider>
			) : null}
			<div className="dynamic-table__table-item">
				{mobile ? <h3>Таблица работ с прокруткой вправо</h3> : null}
				<div className="dynamic-table__wrapper">
					<table className="dynamic-table">
						<thead className="dynamic-table__head">
							<tr>
								<th className="date" scope="col">
									Дата
								</th>
								<th scope="col">Тип</th>
								<th scope="col">Категория</th>
								<th className="half-width" scope="col">
									Количество
								</th>
								<th scope="col">Дополнительно</th>
							</tr>
							{mobile ? null : (
								<tr
									className={
										newShow
											? 'dynamic-table__add-btn hidden'
											: 'dynamic-table__add-btn'
									}
									onClick={() => {
										setNewShow(!newShow)
									}}
								>
									<td>
										<div className="plus-icon">
											<svg width="13" height="13">
												<path
													d="M6 6V.5a.5.5 0 0 1 1 0V6h5.5a.5.5 0 1 1 0 1H7v5.5a.5.5 0 1 1-1 0V7H.5a.5.5 0 0 1 0-1H6z"
													fill="currentColor"
													fillRule="evenodd"
												></path>
											</svg>
										</div>
										Добавить запись
									</td>
								</tr>
							)}
						</thead>
						<tbody>
							<Context.Provider
								value={{
									api,
									accountData,
									newShow,
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
								}}
							>
								{mobile ? null : (
									<WorkSubmitter searchData={searchData}></WorkSubmitter>
								)}
							</Context.Provider>

							{works.map((item) => {
								return (
									<tr className="dynamic-table__row" key={`${item.id}`}>
										<td>
											<div className="date">{item.date}</div>
										</td>
										<td>{item.work_name}</td>
										<td>{item.work_category}</td>
										<td>
											<div className="half-width">{item.count}</div>
										</td>
										<td>{item.object_number}</td>
										<td
											className={`dynamic-table__actions ${
												mobile ? 'dynamic-table__actions_mobile' : ''
											}`}
										>
											<button
												className="dynamic-table__actions__del-btn"
												title="Удалить"
												onClick={() => {
													deleteWork(item.id)
												}}
												disabled={editMode}
											>
												<svg
													xmlns="http://www.w3.org/2000/svg"
													width="24"
													height="24"
													viewBox="0 0 24 24"
													fill="currentColor"
													fillRule="evenodd"
												>
													<path d="M15 2H9c-1.103 0-2 .897-2 2v2H3v2h2v12c0 1.103.897 2 2 2h10c1.103 0 2-.897 2-2V8h2V6h-4V4c0-1.103-.897-2-2-2zM9 4h6v2H9V4zm8 16H7V8h10v12z"></path>
												</svg>
											</button>
											<button
												className="dynamic-table__actions__edit-btn"
												title="Изменить"
												onClick={() => {
													changeWork(
														item.full_date,
														item.work_name,
														item.work_category,
														item.id,
														item.count,
														item.object_number
													)
												}}
											>
												<svg
													xmlns="http://www.w3.org/2000/svg"
													width="24"
													height="24"
													viewBox="0 0 24 24"
													fill="currentColor"
													fillRule="evenodd"
												>
													<path d="M19.045 7.401c.378-.378.586-.88.586-1.414s-.208-1.036-.586-1.414l-1.586-1.586c-.378-.378-.88-.586-1.414-.586s-1.036.208-1.413.585L4 13.585V18h4.413L19.045 7.401zm-3-3 1.587 1.585-1.59 1.584-1.586-1.585 1.589-1.584zM6 16v-1.585l7.04-7.018 1.586 1.586L7.587 16H6zm-2 4h16v2H4z"></path>
												</svg>
											</button>
										</td>
									</tr>
								)
							})}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	)
}
