// Ejemplo de Patrón Repositorio en Dart (Flutter) adaptado desde el C# Backend
// Ubicación: lib/core/data/repository/base_api_repository.dart

import 'package:dio/dio.dart';

/// Interfaz base para los repositorios en Flutter que consumen el API en C#.
/// Esta es la traducción conceptual de ITransactionRepositoryBase<T>.
abstract class ITransactionRepositoryBase<T> {
  Future<T?> getById(int id);
  Future<List<T>> getAll();
  
  /// Equivalente a FindAll() con parámetros query y paginación en C#
  Future<List<T>> findAll({
    Map<String, dynamic>? queryParams,
    int? skip,
    int? take,
    String? orderBy,
    String? orderByDirection,
  });

  Future<T> add(T entity);
  Future<List<T>> addRange(List<T> entities);
  Future<T> update(T entity);
  Future<void> delete(int id);
}

/// Implementación base genérica usando Dio para consumir la API de C#.
/// Se espera que T tenga métodos para serializar/deserializar (ej. fromJson, toJson).
abstract class ApiRepositoryBase<T> implements ITransactionRepositoryBase<T> {
  final Dio _dio;
  final String _endpoint;

  ApiRepositoryBase(this._dio, this._endpoint);

  /// Método abstracto que las clases hijas deben implementar para convertir el JSON al Objeto T
  T fromJson(Map<String, dynamic> json);

  /// Método abstracto que las clases hijas deben implementar para convertir Objeto T a JSON
  Map<String, dynamic> toJson(T entity);

  @override
  Future<T?> getById(int id) async {
    try {
      final response = await _dio.get('$_endpoint/$id');
      if (response.statusCode == 200 && response.data != null) {
        return fromJson(response.data);
      }
      return null;
    } catch (e) {
      // Manejar el error y lanzar excepciones de dominio (Domain Exceptions)
      rethrow;
    }
  }

  @override
  Future<List<T>> getAll() async {
    try {
      final response = await _dio.get(_endpoint);
      if (response.statusCode == 200 && response.data is List) {
        return (response.data as List).map((e) => fromJson(e)).toList();
      }
      return [];
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<List<T>> findAll({
    Map<String, dynamic>? queryParams,
    int? skip,
    int? take,
    String? orderBy,
    String? orderByDirection,
  }) async {
    try {
      // Preparar los query parameters para enviarlos al API de C#
      final Map<String, dynamic> params = queryParams ?? {};
      if (skip != null) params['skip'] = skip;
      if (take != null) params['take'] = take;
      if (orderBy != null) params['orderBy'] = orderBy;
      if (orderByDirection != null) params['orderByDirection'] = orderByDirection;

      final response = await _dio.get(_endpoint, queryParameters: params);
      if (response.statusCode == 200 && response.data is List) {
        return (response.data as List).map((e) => fromJson(e)).toList();
      }
      return [];
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<T> add(T entity) async {
    try {
      final response = await _dio.post(_endpoint, data: toJson(entity));
      return fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<List<T>> addRange(List<T> entities) async {
    try {
      final data = entities.map((e) => toJson(e)).toList();
      final response = await _dio.post('$_endpoint/range', data: data);
      return (response.data as List).map((e) => fromJson(e)).toList();
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<T> update(T entity) async {
    try {
      final response = await _dio.put(_endpoint, data: toJson(entity));
      return fromJson(response.data);
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<void> delete(int id) async {
    try {
      await _dio.delete('$_endpoint/$id');
    } catch (e) {
      rethrow;
    }
  }
}
