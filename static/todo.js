$(function(){
	// 创建todo项的模型
	var Todo = Backbone.Model.extend({
		// todo 默认项
		defaults: function(){
			return {
				title: "empty todo...",
				order: Todos.nextOrder(),
				done: false
			};
		},

		//确保每个todo都有title
		initialize: function(){
			if(!this.get("title")){
				this.set({"title": this.defaults().title});
			}
		},

		// 改变done状态
		toggle: function(){
			this.save({done: !this.get("done")});
		},

	});

	//创建todo项的集合
	var TodoList = Backbone.Collection.extend({

		model: Todo,

		// RethinkDB server
		url: '/todos',

		// 过滤出所有已经完成的todo
		done: function(){
			return this.filter(function(todo){ return todo.get('done'); });
		},

		// 过滤出所有未完成的todo
		remaining: function(){
			return this.without.apply(this, this.done());
		},

		// 在数据库中的todo是按无序GUID排列，下面写一个order方法生成order id
		nextOrder: function(){
			if (!this.length) return 1;
			return this.last().get('order') + 1;
		},

		// todo项按照插入顺序排序
		comparator: function(todo){
			return todo.get('order');
		},

	});

	// 创建集合的全局变量
	var Todos = new TodoList;
});