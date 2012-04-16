/**!
 * @license jQRangeSlider
 * A javascript slider selector that supports dates
 *
 * Copyright (C) Guillaume Gautreau 2012
 * Dual licensed under the MIT or GPL Version 2 licenses.
 *
 */

(function ($, undefined) {
	"use strict";
	
	$.widget("ui.dateRangeSlider", $.ui.rangeSlider, {
		options: {
			bounds: {min: new Date(2010,0,1), max: new Date(2012,0,1)},
			defaultValues: {min: new Date(2010,1,11), max: new Date(2011,1,11)}
		},

		_create: function(){
			$.ui.rangeSlider.prototype._create.apply(this);

			this.element.addClass("ui-dateRangeSlider");
		},

		destroy: function(){
			this.element.removeClass("ui-dateRangeSlider");
			$.ui.rangeSlider.prototype.destroy.apply(this);
		},

		_setOption: function(key, value){
			if ((key === "defaultValues" || key === "bounds") && typeof value !== "undefined" && value !== null && typeof value.min !== "undefined" && typeof value.max !== "undefined" && value.min instanceof Date && value.max instanceof Date){
				$.ui.rangeSlider.prototype._setOption.apply(this, [key, {min:value.min.valueOf(), max:value.max.valueOf()}]);
			}else{
				$.ui.rangeSlider.prototype._setOption.apply(this, this._toArray(arguments));
			}
		},

		option: function(key, value){
			if (key === "bounds" || key === "defaultValues"){
				var result = $.ui.rangeSlider.prototype.option.apply(this, arguments);

				return {min:new Date(result.min), max:new Date(result.max)};
			}

			return $.ui.rangeSlider.prototype.option.apply(this, this._toArray(arguments));
		},

		_defaultFormat: function(value){
			var month = value.getMonth() + 1,
				day = value.getDate();
			return "" + value.getFullYear() + "-" + (month < 10 ? "0" + month : month) + "-" + (day < 10 ? "0" + day : day);
		},

		_format: function(value){
			return $.ui.rangeSlider.prototype._format.apply(this, [new Date(value)]);
		},

		values: function(min, max){
			var values = null;
			
			if (typeof min !== "undefined" && typeof max !== "undefined" && min instanceof Date && max instanceof Date)
			{
				values = $.ui.rangeSlider.prototype.values.apply(this, [min.valueOf(), max.valueOf()]);
			}else{
				values = $.ui.rangeSlider.prototype.values.apply(this, this._toArray(arguments));
			}

			return {min: new Date(values.min), max: new Date(values.max)};
		},

		min: function(min){
			if (typeof min !== "undefined" && min instanceof Date){
				return new Date($.ui.rangeSlider.prototype.min.apply(this, [min.valueOf()]));
			}

			return new Date($.ui.rangeSlider.prototype.min.apply(this));
		},

		max: function(max){
			if (typeof max !== "undefined" && max instanceof Date){
				return new Date($.ui.rangeSlider.prototype.max.apply(this, [max.valueOf()]));
			}

			return new Date($.ui.rangeSlider.prototype.max.apply(this));
		},
		
		bounds: function(min, max){
			var result;
			
			if (typeof min !== "undefined" && min instanceof Date
						&& typeof max !== "undefined" && max instanceof Date) {
				result = $.ui.rangeSlider.prototype.bounds.apply(this, [min.valueOf(), max.valueOf()]);
			} else {
				result = $.ui.rangeSlider.prototype.bounds.apply(this, this._toArray(arguments));
			}
			
			return {min: new Date(result.min), max: new Date(result.max)};
		},

		_toArray: function(argsObject){
			return Array.prototype.slice.call(argsObject);
		}
	});
})(jQuery);